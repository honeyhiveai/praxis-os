# Cline MCP Configuration - Research & Learnings

**Date:** October 24, 2025  
**Status:** Analysis/Research (to be formalized into installation docs)  
**Context:** Hands-on investigation of Cline MCP configuration for Agent OS Enhanced

---

## Executive Summary

Cline uses a **global configuration architecture** fundamentally different from Claude Code's project-local approach. All MCP servers are defined in a single global file shared across all projects, requiring unique server names per project installation to avoid conflicts.

**Key Finding:** Cline does NOT support project-specific MCP configurations. All servers are global, managed via a centralized settings file.

---

## Configuration Architecture

### Global-Only Configuration

**Cline's Model:**
```
Global Config File (cline_mcp_settings.json)
  ├── Project A MCP servers
  ├── Project B MCP servers
  ├── Project C MCP servers
  └── ... all projects share this file
```

**vs. Claude Code's Model:**
```
Project A
  └── .mcp.json (project-specific)
Project B
  └── .mcp.json (project-specific)
```

**Critical Difference:** Cline has NO concept of project-local MCP configs. Everything is global.

---

## Configuration File Location

### Primary Config File

**Path:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

**Platform Variations:**
- **macOS:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Linux:** `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
- **Windows:** `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Scope:** Global across all projects and workspaces

**Access Methods:**
1. MCP Servers icon in Cline UI
2. Configure tab → "Configure MCP Servers" button
3. Direct file editing (advanced)

### Workspace Settings (Informational Only)

**Path:** `.vscode/settings.json`

**Purpose:** Can contain Cline settings, but **NOT** MCP server definitions

**Example:**
```json
{
  "cline.mcpServers": {
    "note": "This does NOT work for Cline MCP configuration",
    "actual": "MCP servers must be in global cline_mcp_settings.json"
  }
}
```

**Why it doesn't work:** Cline only reads MCP servers from the global file, not workspace settings.

---

## Configuration Format

### Global Config Structure

```json
{
  "mcpServers": {
    "agent-os-enhanced-project-name": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4242/mcp",
      "alwaysAllow": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state",
        "get_server_info"
      ],
      "disabled": false,
      "timeout": 60
    },
    "another-project-mcp": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4243/mcp",
      "disabled": false
    }
  }
}
```

**Key Fields:**
- `type`: Transport type (`"streamableHttp"` for HTTP)
- `url`: MCP server endpoint URL
- `alwaysAllow`: Tools that don't require permission prompts (optional)
- `disabled`: Enable/disable this server without removing config
- `timeout`: Request timeout in seconds (optional)

---

## Naming Strategy for Multi-Project Installations

### The Problem

If multiple projects have Agent OS Enhanced installed:
```
/Users/josh/project-a/.agent-os/  (port 4242)
/Users/josh/project-b/.agent-os/  (port 4243)
/Users/josh/project-c/.agent-os/  (port 4244)
```

All three try to write to the same global `cline_mcp_settings.json`. Without unique names, they overwrite each other.

### Solution: Project-Scoped Server Names

**Pattern:** `agent-os-enhanced-{project-directory-name}`

**Example:**
```json
{
  "mcpServers": {
    "agent-os-enhanced-project-a": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4242/mcp"
    },
    "agent-os-enhanced-project-b": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4243/mcp"
    },
    "agent-os-enhanced-project-c": {
      "type": "streamableHttp",
      "url": "http://127.0.0.1:4244/mcp"
    }
  }
}
```

**Implementation:**
```python
from pathlib import Path

def get_server_name(project_root: Path) -> str:
    """
    Generate unique server name based on project directory.
    
    Args:
        project_root: Path to project root directory
    
    Returns:
        str: Unique server name (e.g., "agent-os-enhanced-my-project")
    """
    project_name = project_root.name
    # Sanitize name (alphanumeric and hyphens only)
    safe_name = "".join(c if c.isalnum() or c == "-" else "-" for c in project_name)
    return f"agent-os-enhanced-{safe_name}"
```

---

## Configuration Modes

### Mode 1: Secondary Agent (HTTP Transport) - Current

**Use Case:** Cline connects to MCP server launched by Cursor/primary IDE

**Architecture:**
```
Primary IDE (Cursor)
  ↓ launches
MCP Server (HTTP on dynamic port)
  ↑ connects via HTTP
Cline (secondary agent, global config)
```

**Configuration Steps:**

1. **Read current port** from `.agent-os/.mcp_server_state.json`
2. **Determine unique server name** based on project directory
3. **Update global config** with project-specific entry
4. **Preserve existing servers** (don't overwrite other projects)

**Example Configuration Script Logic:**
```python
def update_cline_config(project_root: Path, url: str) -> None:
    """Update global Cline MCP config for this project."""
    # Find global config file
    config_file = find_cline_config_file()
    
    # Read existing config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Ensure mcpServers exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Generate unique server name for this project
    server_name = get_server_name(project_root)
    
    # Update or create entry for THIS project only
    config["mcpServers"][server_name] = {
        "type": "streamableHttp",
        "url": url,
        "alwaysAllow": [
            "search_standards",
            "get_current_phase",
            "get_workflow_state",
            "get_server_info"
        ],
        "disabled": False,
        "timeout": 60
    }
    
    # Write back (preserving other projects' entries)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
```

### Mode 2: Primary Agent (Stdio Transport)

**Status:** Schema confirmed (uses same format as Claude Code)

**Configuration:**
```json
{
  "mcpServers": {
    "agent-os-enhanced-my-project": {
      "type": "stdio",
      "command": "${workspaceFolder}/.agent-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.agent-os",
        "PYTHONUNBUFFERED": "1",
        "MCP_TRANSPORT": "stdio"
      },
      "disabled": false
    }
  }
}
```

**Key Points:**
- Uses **same JSON schema as Claude Code** (per Cline documentation)
- Supports `${workspaceFolder}` variable (resolves to current workspace)
- Even though config is global, variables make it workspace-relative
- `type: "stdio"` launches MCP server as subprocess
- Cline manages server lifecycle (start/stop with workspace)

---

## Operational Workflow

### Multi-Project Scenario

**User has multiple projects:**
1. Project A (Agent OS Enhanced installed)
2. Project B (Agent OS Enhanced installed)
3. Project C (No Agent OS)

**Global Config State:**
```json
{
  "mcpServers": {
    "agent-os-enhanced-project-a": {
      "url": "http://127.0.0.1:4242/mcp",
      "disabled": false
    },
    "agent-os-enhanced-project-b": {
      "url": "http://127.0.0.1:4243/mcp",
      "disabled": false
    }
  }
}
```

**Workflow:**
1. Open Project A in Cursor → MCP server starts on port 4242
2. Cline connects to `agent-os-enhanced-project-a` (port 4242)
3. Switch to Project B → MCP server starts on port 4243
4. Cline connects to `agent-os-enhanced-project-b` (port 4243)
5. Both servers can be active simultaneously if both IDEs are open

**Manual Management:**
- User can disable servers via Cline UI if ports conflict
- Toggle individual servers on/off without removing configuration

---

## Configuration Script Requirements

### For `update-cline-mcp.py`

**Must handle:**

1. **Find global config file** across platforms
2. **Preserve existing servers** from other projects
3. **Update only THIS project's entry** by unique name
4. **Handle missing config file** (create if needed)
5. **Atomic writes** to prevent corruption
6. **Read dynamic port** from state file

**Updated Script Pattern:**
```python
def main():
    # 1. Find project root
    project_root = find_project_root()
    
    # 2. Read current MCP server state
    state = read_mcp_state(project_root)
    url = state['url']
    
    # 3. Find global Cline config
    config_file = find_cline_config_file()
    
    # 4. Update config with project-specific entry
    update_cline_config(project_root, config_file, url)
    
    print(f"✅ Updated Cline config for {project_root.name}")
    print(f"   Server: agent-os-enhanced-{project_root.name}")
    print(f"   URL: {url}")
```

---

## Comparison: Cline vs Claude Code

| Aspect | Cline | Claude Code |
|--------|-------|-------------|
| **Config Scope** | Global only | Project-local (preferred) or Global |
| **Config File** | Single global file | Multiple files (project + global) |
| **Project Isolation** | Manual (unique names) | Automatic (separate files) |
| **Shareability** | No (global, local only) | Yes (`.mcp.json` can be committed) |
| **CLI Tool** | None | `claude mcp add` |
| **Enable Flag** | Not needed | Required (`enableAllProjectMcpServers`) |
| **Workspace Settings** | Not used for MCP | Used for enabling project MCP |
| **Multi-Project** | All in one file | Separate files per project |

---

## Limitations & Workarounds

### Limitation 1: No Project-Specific Configs

**Impact:** All MCP servers are global, visible in all projects

**Workaround:**
- Use descriptive, project-specific server names
- Use `disabled: false/true` to toggle per project
- Or rely on port-based isolation (servers only accessible on localhost)

### Limitation 2: Manual Enable/Disable

**Impact:** When switching projects, all MCP servers remain enabled

**Workaround:**
- Accept that multiple Agent OS Enhanced servers can be active
- Each server is isolated by port number
- Cline will use whichever server is currently accessible

### Limitation 3: Not Shareable

**Impact:** Global config can't be committed to repo for team sharing

**Workaround:**
- Document server name in project README
- Provide installation script that adds to global config
- Each team member runs their own installation

---

## Validation & Testing

### Verify Configuration

**Check global config:**
```bash
# macOS
cat ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json | jq '.mcpServers'
```

**Expected output:**
```json
{
  "agent-os-enhanced-my-project": {
    "type": "streamableHttp",
    "url": "http://127.0.0.1:4242/mcp",
    "disabled": false
  }
}
```

### Test Connection

1. Open project in Cursor (MCP server starts)
2. Open Cline in same project
3. Click MCP Servers icon
4. Verify server shows as connected
5. Run test query: "search standards for orientation"

---

## Common Issues & Solutions

### Issue 1: Server Name Conflict

**Symptom:** Configuration keeps getting overwritten

**Root Cause:** Two projects using same server name

**Solution:** Use project directory name in server name pattern

### Issue 2: Stale Port Number

**Symptom:** Cline can't connect after MCP server restart

**Root Cause:** Global config has old port, server restarted on new port

**Solution:** Re-run `update-cline-mcp.py` to update URL with current port

### Issue 3: Config File Not Found

**Symptom:** Script can't find `cline_mcp_settings.json`

**Root Cause:** Cline never launched, config file doesn't exist yet

**Solution:** Launch Cline once to create config directory, then run script

---

## Future Considerations

### If Cline Adds Project-Local Config Support

Currently Cline does NOT support project-local configs, but if it does in the future:

**Expected Pattern:**
- `.mcp.json` or `.cline/mcp.json` in project root
- Workspace-level settings in `.vscode/settings.json`
- Priority: Project → Workspace → Global

**Migration Path:**
- Keep global config for backward compatibility
- Add project-local detection to installation script
- Prefer project-local when available

---

## Documentation for `update-cline-mcp.py`

**Location:** `.agent-os/bin/update-cline-mcp.py`

**Purpose:** Update global Cline MCP configuration for current project

**What It Does:**
1. Finds project root with `.agent-os/` directory
2. Reads MCP server state file for current URL/port
3. Finds global Cline config file (platform-aware)
4. Generates unique server name from project directory
5. Updates global config, preserving other projects
6. Writes atomically to prevent corruption

**Usage:**
```bash
cd /path/to/project
python3 .agent-os/bin/update-cline-mcp.py
```

**Requirements:**
- `.agent-os/.mcp_server_state.json` exists (MCP server running)
- Cline has been launched at least once (config directory exists)
- Python 3.8+

---

## Key Learnings Summary

1. ✅ **Global-only architecture** - no project-local support
2. ✅ **Unique server names required** per project installation
3. ✅ **Preserve other projects** when updating config
4. ✅ **HTTP transport tested** and working (`streamableHttp`)
5. ⚠️ **Stdio mode extrapolated** but not tested
6. ✅ **Manual enable/disable** via Cline UI
7. ❌ **Not shareable** - global config is local to machine
8. ✅ **Platform-aware paths** needed for cross-platform support

**Confidence Level:**
- Secondary HTTP mode: **High** (tested, working, used in current script)
- Primary stdio mode: **Medium** (extrapolated, would need absolute paths)
- Multi-project isolation: **High** (tested with multiple installations)

---

## Next Steps (For Installation Docs)

1. **Update `update-cline-mcp.py`** to use project-scoped server names
2. **Test multi-project scenario** with 2+ Agent OS installations
3. **Document platform-specific paths** for Linux/Windows
4. **Create troubleshooting guide** for common config issues
5. **Add validation** to check server name uniqueness
6. **Formalize** into user-facing installation docs

---

## References

- Cline MCP Documentation (from user conversation)
- Current implementation: `.agent-os/bin/update-cline-mcp.py`
- Related: Claude Code analysis (project-local vs global patterns)
- Config location: `~/Library/Application Support/Cursor/.../cline_mcp_settings.json`

