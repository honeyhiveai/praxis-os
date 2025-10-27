# Claude Code MCP Configuration - Research & Learnings

**Date:** October 24, 2025  
**Status:** Analysis/Research (to be formalized into installation docs)  
**Context:** Hands-on investigation of Claude Code MCP configuration for Agent OS Enhanced

---

## Executive Summary

Through hands-on testing, we discovered Claude Code's MCP configuration patterns for both secondary agent (HTTP) and primary agent (stdio) modes. This document captures configuration file locations, required settings, and behavioral differences between CLI and VS Code extension.

**Key Finding:** Claude Code requires **THREE** configuration touchpoints to enable project-scoped MCP servers in VS Code extension mode.

---

## Server Naming Psychology

### The Impact of Names on AI Agent Behavior

**Critical Insight:** The MCP server name significantly influences AI agent decision-making and tool usage patterns.

**Generic Naming (`agent-os-rag`):**
```
Mental Model:
"This is a RAG tool" 
→ Generic capability
→ Could be for any project
→ Feels like external dependency
→ Requires inference: "Is this relevant?"
```

**Project-Aligned Naming (`praxis-os`):**
```
Mental Model:
"This is THE praxis-os assistant"
→ Project-specific identity
→ Obviously for THIS project
→ Feels like native capability
→ Instant relevance: "This is the source"
```

**Observable Behavioral Differences:**

| Aspect | Generic Name | Project Name |
|--------|-------------|--------------|
| First instinct | "Should I use this tool?" | "Query the project knowledge" |
| Mental model | Tool among tools | Native project capability |
| Context association | Requires inference | Instant recognition |
| Multi-project clarity | Ambiguous | Obvious which project |
| Query frequency | May hesitate | More instinctive |

**Recommendation:** Use project directory name as server name for maximum psychological alignment.

**Example Pattern:**
```json
{
  "mcpServers": {
    "praxis-os": {  // ← Project name
      "type": "http",
      "url": "http://127.0.0.1:4242/mcp"
    }
  }
}
```

**Why This Matters:**
- Name creates identity anchor: "I'm in X project" → "Query X knowledge base"
- Stronger project-tool association increases usage frequency
- Multi-project scenarios become clearer (each project = unique tool name)
- Feels like querying "the project" not "a tool"

---

## Configuration Modes

### Mode 1: Secondary Agent (HTTP Transport)

**Use Case:** Claude Code connects to existing MCP server launched by another IDE (Cursor/VS Code with Cline)

**Architecture:**
```
Primary IDE (Cursor)
  ↓ launches
MCP Server (HTTP on dynamic port)
  ↑ connects via HTTP
Claude Code (secondary agent)
```

**Required Configuration Files:**

#### 1. `.mcp.json` (Project-Local MCP Server Definition)
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "type": "http",
      "url": "http://127.0.0.1:4242/mcp"
    }
  }
}
```

**Purpose:** Defines the MCP server connection  
**Scope:** Project-local (shareable, can be committed)  
**Created by:** `claude mcp add --scope project --transport http agent-os-rag <url>`

#### 2. `.claude/settings.local.json` (CLI Settings)
```json
{
  "enableAllProjectMcpServers": true
}
```

**Purpose:** Enables Claude Code CLI to respect project-local `.mcp.json`  
**Scope:** Project-local  
**Required for:** CLI (`claude` command) to see project MCP servers

#### 3. `.vscode/settings.json` (VS Code Workspace Settings)
```json
{
  "claudeCode.enableProjectMcpServers": true
}
```

**Purpose:** Enables Claude Code **VS Code extension** to respect project-local `.mcp.json`  
**Scope:** Workspace  
**Required for:** VS Code extension to see project MCP servers  
**Critical:** Without this, VS Code extension ignores `.mcp.json` even though CLI works

---

## Configuration Priority

Claude Code resolves MCP servers in this order:

1. **Project `.mcp.json`** (if `enableAllProjectMcpServers: true`) ← Preferred
2. **User `~/.claude.json`** (project-specific section) ← Fallback
3. **User `~/.claude.json`** (global section) ← Last resort

**Best Practice:** Use project `.mcp.json` for shareable, team-wide configuration.

---

## Configuration Methods

### Method 1: Official CLI (Recommended)

```bash
cd /path/to/project

# Add to project-local config
claude mcp add --scope project --transport http agent-os-rag http://127.0.0.1:4242/mcp

# Verify
cat .mcp.json
```

**Pros:**
- Official Anthropic tooling
- Validated configuration format
- Automatic schema handling

**Cons:**
- Requires `claude` CLI installed
- May fail if server already exists (benign)

### Method 2: Manual JSON Editing (Fallback)

```python
import json
from pathlib import Path

project_root = Path.cwd()
mcp_json = project_root / ".mcp.json"

config = {
    "mcpServers": {
        "agent-os-rag": {
            "type": "http",
            "url": "http://127.0.0.1:4242/mcp"
        }
    }
}

with open(mcp_json, 'w') as f:
    json.dump(config, f, indent=2)
```

**Use when:** CLI not available or fails

---

## Mode 2: Primary Agent (Stdio Transport) - Extrapolated

**Use Case:** Claude Code launches and manages its own MCP server process

**Architecture:**
```
Claude Code (primary agent)
  ↓ launches via stdio
MCP Server Process (subprocess)
  ↑ communicates via stdin/stdout
Claude Code
```

**Expected Configuration:**

#### `.mcp.json` (Project-Local)
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "type": "stdio",
      "command": "/path/to/project/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

**Key Differences from HTTP Mode:**
- `"type": "stdio"` (not `"http"`)
- Includes `"command"` and `"args"` to launch process
- Environment variables for Python process
- Uses `${workspaceFolder}` variable (VS Code standard)

**CLI Command (Expected):**
```bash
claude mcp add --scope project --transport stdio agent-os-rag \
  --env PROJECT_ROOT='${workspaceFolder}' \
  --env PYTHONPATH='${workspaceFolder}/.praxis-os' \
  --env PYTHONUNBUFFERED='1' \
  --env MCP_TRANSPORT='stdio' \
  -- /path/to/.praxis-os/venv/bin/python -m mcp_server
```

**Settings Files:** Same as HTTP mode (`.claude/settings.local.json` and `.vscode/settings.json`)

---

## Behavioral Differences

### CLI vs VS Code Extension

| Aspect | CLI (`claude` command) | VS Code Extension |
|--------|----------------------|-------------------|
| Config read | `.claude/settings.local.json` | `.vscode/settings.json` |
| Enable flag | `enableAllProjectMcpServers` | `claudeCode.enableProjectMcpServers` |
| `.mcp.json` support | ✅ (if enabled) | ✅ (if enabled) |
| Global config | `~/.claude.json` | `~/.claude.json` |
| Behavior | Works after flag set | **Requires workspace setting too** |

**Critical Insight:** The VS Code extension needs **both** `.claude/settings.local.json` AND `.vscode/settings.json` to enable project MCP servers. The CLI only needs `.claude/settings.local.json`.

---

## Dynamic Port Handling

For secondary agent HTTP mode, the MCP server port is dynamic (allocated by OS). Solution:

**State File:** `.praxis-os/.mcp_server_state.json`
```json
{
  "url": "http://127.0.0.1:4242/mcp",
  "port": 4242,
  "transport": "http",
  "started_at": "2025-10-24T10:30:00Z",
  "pid": 12345
}
```

**Configuration Script Pattern:**
1. Primary IDE starts MCP server on dynamic port
2. MCP server writes state file with allocated port
3. Secondary agent configuration script reads state file
4. Script runs `claude mcp add` with current port URL

**Implementation:** `.praxis-os/bin/configure-claude-code-mcp.py`

---

## Validation Checklist

After configuration, verify with:

### CLI Validation
```bash
# Should show agent-os-rag server
claude mcp list

# Test query
claude "search standards for orientation"
```

### VS Code Extension Validation
1. Reload VS Code window (Cmd+Shift+P → "Reload Window")
2. Open Claude Code extension
3. Ask: "what mcp servers do you see"
4. Expected: Should list `agent-os-rag` with connection status

---

## Common Issues & Solutions

### Issue 1: VS Code Extension Doesn't See MCP Server

**Symptom:** CLI works, VS Code extension doesn't show MCP server

**Root Cause:** Missing `.vscode/settings.json` setting

**Solution:**
```json
// .vscode/settings.json
{
  "claudeCode.enableProjectMcpServers": true
}
```

### Issue 2: CLI Command Fails (Server Already Exists)

**Symptom:** `claude mcp add` returns error about existing server

**Root Cause:** Server already configured in global or project config

**Solution:** Use manual JSON editing fallback or remove existing entry first

### Issue 3: Stale Port Number

**Symptom:** Claude Code tries to connect to old port after MCP server restart

**Root Cause:** `.mcp.json` has hardcoded old port, server restarted on new port

**Solution:** Re-run configuration script to update `.mcp.json` with current port from state file

---

## Testing Strategy

### Test Matrix

| Mode | Transport | Launch Method | Config Files | Status |
|------|-----------|--------------|--------------|--------|
| Secondary | HTTP | External (Cursor) | 3 files | ✅ Tested |
| Primary | Stdio | Claude Code | 3 files | ⚠️ Extrapolated |
| Secondary | HTTP | External (Cline) | 3 files | ✅ Implied working |

### Test Scenarios

**Scenario 1: Fresh Installation (Secondary Agent)**
1. Install Agent OS Enhanced in Cursor
2. Run `configure-claude-code-mcp.py`
3. Reload VS Code window
4. Open Claude Code extension
5. Verify MCP server connection
6. Run test query

**Scenario 2: Port Change (Secondary Agent)**
1. Stop MCP server (close primary IDE)
2. Restart primary IDE (MCP server gets new port)
3. Re-run configuration script
4. Verify `.mcp.json` updated with new port
5. Reload Claude Code
6. Verify connection works

**Scenario 3: Primary Agent Stdio (Not Yet Tested)**
1. Configure `.mcp.json` with stdio settings
2. Set environment variables
3. Open Claude Code
4. Verify MCP server launches as subprocess
5. Run test query

---

## Documentation for `configure-claude-code-mcp.py`

**Location:** `.praxis-os/bin/configure-claude-code-mcp.py`

**Purpose:** Automated configuration of Claude Code for secondary agent HTTP mode

**What It Does:**
1. Finds project root with `.praxis-os/` directory
2. Reads MCP server state file for current port
3. Enables project MCP in `.claude/settings.local.json`
4. Enables project MCP in `.vscode/settings.json`
5. Updates `.mcp.json` via `claude mcp add --scope project`
6. Falls back to manual JSON editing if CLI fails

**Usage:**
```bash
cd /path/to/project
python3 .praxis-os/bin/configure-claude-code-mcp.py
```

**Requirements:**
- `.praxis-os/.mcp_server_state.json` exists (MCP server running)
- `claude` CLI installed (recommended, has fallback)
- Python 3.8+

---

## Next Steps (For Installation Docs)

1. **Formalize** this research into installation guide
2. **Create** primary agent stdio mode configuration script
3. **Test** primary agent mode in real environment
4. **Document** troubleshooting steps with screenshots
5. **Add** validation tests to installation script
6. **Create** user-facing docs with step-by-step instructions

---

## References

- [Claude Code MCP Documentation](https://docs.claude.com/en/docs/claude-code/mcp.md)
- Official CLI: `claude mcp add --help`
- Agent OS Enhanced: `.praxis-os/bin/configure-claude-code-mcp.py`
- Related: `.praxis-os/bin/update-cline-mcp.py` (similar pattern)

---

## Key Learnings Summary

1. ✅ **Three config files required** for VS Code extension support
2. ✅ **CLI vs extension** have different settings requirements
3. ✅ **Official CLI preferred** but manual fallback works
4. ✅ **Dynamic ports** require state file + re-configuration
5. ✅ **Project-local config** is shareable and preferred
6. ⚠️ **Stdio mode** extrapolated but not yet tested
7. ✅ **HTTP mode** fully tested and working

**Confidence Level:**
- Secondary HTTP mode: **High** (tested, working)
- Primary stdio mode: **Medium** (extrapolated from patterns, needs testing)

