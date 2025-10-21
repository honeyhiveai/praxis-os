# IDE Configuration Guide for Dual-Transport MCP Server

**Feature:** Dual-Transport Architecture  
**Date:** 2025-10-11  
**Status:** Production Ready

---

## Overview

The Agent OS MCP server now supports **dual-transport mode**, allowing:
- **Main IDE** (Cursor, Windsurf, etc.) connects via **stdio**
- **Sub-agents** (Cline, Aider, custom scripts) connect via **HTTP**

This enables multi-agent collaboration within a single project without port conflicts or resource duplication.

---

## Transport Modes

The MCP server supports three transport modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| `stdio` | Standard input/output only | Single IDE, no sub-agents (default, backwards compatible) |
| `http` | HTTP endpoint only | Server-only mode, no direct IDE connection |
| `dual` | Both stdio + HTTP | **Recommended**: Main IDE + sub-agents |

### Recommended Configuration

**Use `dual` mode** for the best experience:
- ✅ Main IDE connects normally via stdio
- ✅ Sub-agents auto-discover via HTTP (no manual port config)
- ✅ Zero-conflict multi-project support (ports auto-allocated)
- ✅ State file enables monitoring and health checks

---

## Cursor Configuration

### Dual-Transport Setup (Recommended)

**File:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "comment": "Dual transport: Cursor uses stdio, sub-agents use HTTP",
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "PYTHONUNBUFFERED": "1"
      },
      "transport": "stdio",
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state"
      ]
    }
  }
}
```

### Legacy Setup (Stdio Only)

For backwards compatibility, omitting `--transport dual` defaults to stdio-only:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server"
      ],
      "transport": "stdio"
    }
  }
}
```

**Note:** Legacy mode works but sub-agents cannot connect.

---

## Windsurf Configuration

Windsurf uses a similar configuration format to Cursor.

**File:** `.windsurf/mcp.json` (or Windsurf settings)

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
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
        "PYTHONPATH": "${workspaceFolder}/.agent-os"
      },
      "transport": "stdio"
    }
  }
}
```

**Key Points:**
- `"transport": "stdio"` tells Windsurf to use stdio
- `"--transport", "dual"` tells the MCP server to also enable HTTP
- Sub-agents can connect via HTTP while Windsurf uses stdio

---

## Claude Desktop Configuration

Claude Desktop uses a slightly different configuration format.

**File (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**File (Windows):** `%APPDATA%\Claude\claude_desktop_config.json`  
**File (Linux):** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "/path/to/your/project/.agent-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "env": {
        "PROJECT_ROOT": "/path/to/your/project",
        "PYTHONPATH": "/path/to/your/project/.agent-os"
      }
    }
  }
}
```

**Important:**
- Replace `/path/to/your/project` with your actual project path
- Use absolute paths (Claude Desktop doesn't support `${workspaceFolder}`)
- On Windows, use backslashes or double forward slashes: `C:\\Users\\...` or `C://Users/...`

---

## Cline Configuration

Cline (sub-agent) should auto-discover the MCP server via the state file. No manual configuration needed!

However, you can manually configure if auto-discovery fails:

**File:** `.cline/mcp_settings.json`

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

**Note:** Port `4242` is the default but will auto-increment if taken. Check `.agent-os/.mcp_server_state.json` for the actual port.

---

## Auto-Discovery for Sub-Agents

Sub-agents can auto-discover the MCP server using the provided utility:

```python
from mcp_server.sub_agents import discover_mcp_server

# Discover server
url = discover_mcp_server()
if url:
    print(f"MCP server found at: {url}")
else:
    print("MCP server not running")
```

The discovery utility:
- ✅ Reads `.agent-os/.mcp_server_state.json`
- ✅ Validates the server process is still alive
- ✅ Returns the HTTP URL or `None`
- ✅ Thread-safe and fast (< 5ms)

---

## Port Management

### Default Port Allocation

- **Preferred port:** `4242` (configurable in `config.yaml`)
- **Range:** `4242-5242` (1000 ports)
- **Allocation:** Auto-increments if port taken
- **Multi-project:** Each project gets unique port (no conflicts)

### State File

**Location:** `.agent-os/.mcp_server_state.json`

**Example:**
```json
{
  "transport": "dual",
  "url": "http://127.0.0.1:4242/mcp",
  "host": "127.0.0.1",
  "port": 4242,
  "path": "/mcp",
  "pid": 12345,
  "project": {
    "name": "agent-os-enhanced",
    "root": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced",
    "agent_os_path": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced/.agent-os"
  },
  "started_at": "2025-10-11T14:30:00Z"
}
```

**Usage:**
- Sub-agents read this file for server URL
- Monitoring tools check PID for liveness
- Multiple projects maintain separate state files

---

## Transport Mode Selection Guide

### When to Use `dual` Mode (Recommended)

✅ **Use dual mode if:**
- You're using Cursor/Windsurf as your main IDE
- You want to use sub-agents (Cline, Aider, custom scripts)
- You're working on a team with multiple agents
- You want monitoring/health check capabilities

### When to Use `stdio` Mode

✅ **Use stdio mode if:**
- You only use a single IDE (backwards compatible)
- You don't need sub-agents
- You want the simplest setup (no HTTP server)

### When to Use `http` Mode

✅ **Use HTTP mode if:**
- You're running a dedicated MCP server (not IDE-attached)
- All clients connect via HTTP
- You're using the server in a containerized environment

---

## Troubleshooting

### Sub-Agent Can't Connect

**Symptom:** Sub-agent reports "MCP server not found"

**Solutions:**
1. **Check server is running:**
   ```bash
   ps aux | grep mcp_server
   ```

2. **Check state file exists:**
   ```bash
   cat .agent-os/.mcp_server_state.json
   ```

3. **Verify PID is alive:**
   ```bash
   kill -0 $(jq '.pid' .agent-os/.mcp_server_state.json)
   ```

4. **Check transport mode:**
   ```bash
   jq '.transport' .agent-os/.mcp_server_state.json
   # Should be "dual" or "http", not "stdio"
   ```

5. **Restart with dual mode:**
   - Update `.cursor/mcp.json` to include `["--transport", "dual"]`
   - Restart Cursor or reload window

### Port Already in Use

**Symptom:** Server fails to start with "Address already in use"

**Solution:** The server auto-increments ports. If it still fails:

1. **Check for stale state file:**
   ```bash
   rm .agent-os/.mcp_server_state.json
   ```

2. **Check what's using the port:**
   ```bash
   lsof -i :4242
   ```

3. **Configure different preferred port:**
   ```yaml
   # .agent-os/config.yaml
   mcp:
     http_port: 5000  # Use different starting port
   ```

### IDE Doesn't Recognize Config

**Symptom:** IDE doesn't load MCP tools

**Solutions:**
1. **Reload IDE window** (Cmd+Shift+P → "Reload Window")
2. **Check file location:**
   - Cursor: `.cursor/mcp.json`
   - Windsurf: `.windsurf/mcp.json`
   - Claude Desktop: See paths above
3. **Validate JSON syntax:** Use `jq` or online validator
4. **Check logs:** IDE console usually shows MCP errors

### Different Port Each Time

**Symptom:** State file shows different port after restart

**This is expected behavior!** Ports are ephemeral:
- Port released on shutdown
- New port allocated on startup
- Sub-agents auto-discover via state file

To use a consistent port:
```yaml
# .agent-os/config.yaml
mcp:
  http_port: 4242  # Preferred port (not guaranteed)
```

---

## Testing Your Configuration

### 1. Start the Server

**Via IDE:** Open your project in Cursor/Windsurf (server starts automatically)

**Via CLI:**
```bash
cd /path/to/your/project
.agent-os/venv/bin/python -m mcp_server --transport dual
```

### 2. Verify State File

```bash
cat .agent-os/.mcp_server_state.json
```

Should show:
- `"transport": "dual"`
- `"url": "http://..."` 
- `"pid": <number>`

### 3. Test Sub-Agent Discovery

```bash
python -m mcp_server.sub_agents.mcp_client_example
```

Should output:
```
✅ Connection successful!
   URL: http://127.0.0.1:4242/mcp
   Tools available: 10
```

### 4. Test from IDE

In Cursor/Windsurf, ask the AI:
```
@agent-os Search for "production code checklist"
```

Should return results from your standards files.

---

## Migration from Stdio-Only

### No Breaking Changes

**Good news:** Existing configs continue to work!

- Old config (without `--transport dual`) → stdio-only mode
- New config (with `--transport dual`) → dual mode
- No data migration needed
- No config file format changes

### Migration Steps

1. **Backup your config:**
   ```bash
   cp .cursor/mcp.json .cursor/mcp.json.backup
   ```

2. **Add dual transport:**
   ```json
   "args": [
     "-m",
     "mcp_server",
     "--transport",
     "dual"
   ]
   ```

3. **Reload IDE window**

4. **Verify state file created:**
   ```bash
   ls -la .agent-os/.mcp_server_state.json
   ```

5. **Test sub-agent connection** (see above)

### Rollback

To rollback to stdio-only:

1. **Remove dual transport flag:**
   ```json
   "args": [
     "-m",
     "mcp_server"
   ]
   ```

2. **Reload IDE window**

3. **Remove state file:**
   ```bash
   rm .agent-os/.mcp_server_state.json
   ```

---

## Best Practices

### ✅ Do's

- ✅ Use `dual` mode for new projects
- ✅ Let sub-agents auto-discover (don't hardcode ports)
- ✅ Use `.gitignore` for `.mcp_server_state.json` (already configured)
- ✅ Set `http_port` in `config.yaml` for preferred port
- ✅ Monitor state file for server health
- ✅ Use `--log-level DEBUG` when troubleshooting

### ❌ Don'ts

- ❌ Don't hardcode ports in sub-agent configs
- ❌ Don't commit `.mcp_server_state.json` to git
- ❌ Don't use `http` mode unless you know why
- ❌ Don't manually edit state file (managed by server)
- ❌ Don't assume port `4242` (use auto-discovery)

---

## Examples by IDE

### Cursor + Cline

**Cursor config (`.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "transport": "stdio"
    }
  }
}
```

**Cline:** Auto-discovers via state file. No config needed!

### Windsurf + Aider

**Windsurf config (`.windsurf/mcp.json`):**
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "transport": "stdio"
    }
  }
}
```

**Aider:** Use Python SDK with auto-discovery:
```python
from mcp_server.sub_agents import discover_mcp_server
url = discover_mcp_server()
# Use url with streamable_http_client
```

### Claude Desktop + Custom Script

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "/absolute/path/to/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"]
    }
  }
}
```

**Custom script:**
```python
import asyncio
from mcp_server.sub_agents.mcp_client_example import connect_and_use_mcp_server

result = asyncio.run(connect_and_use_mcp_server())
print(result)
```

---

## Summary

| Feature | Stdio Mode | HTTP Mode | **Dual Mode** |
|---------|-----------|-----------|---------------|
| Main IDE connection | ✅ | ❌ | ✅ |
| Sub-agent connection | ❌ | ✅ | ✅ |
| Auto-discovery | N/A | Manual | **✅ Automatic** |
| Multi-project support | N/A | Manual ports | **✅ Zero-config** |
| State file | ❌ | ✅ | ✅ |
| Backwards compatible | ✅ | N/A | ✅ |
| **Recommended** | Legacy | Server-only | **✅ Yes** |

**Recommendation:** Use **dual mode** for all new projects. It's backwards compatible, enables multi-agent workflows, and requires no additional configuration.

---

## Support

For issues or questions:
1. Check `.agent-os/specs/2025-10-11-mcp-dual-transport/` for detailed specs
2. See `THREAD-SAFETY.md` for performance and safety considerations
3. Review `mcp_server/sub_agents/mcp_client_example.py` for working examples
4. Check server logs (IDE console or `--log-level DEBUG`)

**State:** ✅ Production Ready (2025-10-11)

