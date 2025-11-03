---
sidebar_position: 0
doc_type: how-to
---

# Agent Integration Overview

Configure prAxIs OS for your specific AI agent and IDE. Choose based on your primary development environment.

## Installation Command Pattern

```bash
"Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> [in <IDE>]"
```

**Examples:**
- `for Cursor` → Cursor IDE (primary, native MCP)
- `for Cline in VS Code` → Cline extension in VS Code (primary)
- `for Cline in Cursor` → Cline as secondary agent (connects to Cursor's MCP server)
- `for Claude Code` → Claude Code CLI (primary, terminal)
- `for Claude Code in VS Code` → Claude Code in VS Code (primary)

## Primary vs Secondary Agents

### Primary Agents (Control MCP Server)

Primary agents **own the MCP server lifecycle** - they start, stop, and manage it:

| Agent | IDE | MCP Connection | Guide |
|-------|-----|----------------|-------|
| **Cursor** | Cursor IDE | Native MCP via `.cursor/mcp.json` | [cursor/](./cursor/) |
| **Cline** | VS Code | MCP via VS Code settings | [cline/vscode.md](./cline/vscode.md) |
| **Claude Code** | Terminal (CLI) | Direct MCP server invocation | [claude-code/terminal.md](./claude-code/terminal.md) |
| **Claude Code** | VS Code | MCP via VS Code integration | [claude-code/vscode.md](./claude-code/vscode.md) |

**When to use primary mode:**
- This is your main AI coding assistant
- You want full control over MCP server
- Single agent workflow

### Secondary Agents (Connect via HTTP)

Secondary agents **connect to an existing MCP server** via HTTP (run by a primary agent):

| Agent | Primary Agent | Connection | Guide |
|-------|---------------|------------|-------|
| **Cline** | Cursor | HTTP to Cursor's MCP server | [cline/cursor.md](./cline/cursor.md) |
| **Claude Code** | Cursor | HTTP to Cursor's MCP server | [claude-code/cursor.md](./claude-code/cursor.md) |

**When to use secondary mode:**
- Multi-agent workflow (Cursor + Cline, for example)
- Primary agent already managing MCP server
- Want specialized agent for specific tasks

**Example multi-agent setup:**
- **Cursor** (primary) - Main development, owns MCP server
- **Cline** (secondary) - Connects to Cursor's MCP via HTTP for specialized tasks

## Quick Decision Tree

```
Do you use Cursor as your main IDE?
├─ YES → Primary: cursor/
│   └─ Want to add Cline? → Secondary: cline/cursor.md
│   └─ Want to add Claude Code? → Secondary: claude-code/cursor.md
│
└─ NO → Do you use VS Code?
    ├─ YES → Primary: cline/vscode.md or claude-code/vscode.md
    └─ NO → Primary: claude-code/terminal.md (CLI)
```

## LLM Model Support

All integrations work with multiple LLM models. Recommended:

- **Claude 3.5 Sonnet** - Best MCP tool calling, recommended
- **GPT-4 Turbo** - Good alternative
- **Claude 3 Opus** - Supported
- **GPT-4** - Supported

**Note**: Tool calling quality varies by model. Claude 3.5 Sonnet has best performance with MCP.

## MCP Server HTTP Mode (For Secondary Agents)

When running secondary agents, the **primary agent** must use `--transport dual` to enable HTTP endpoint:

**In `.cursor/mcp.json`** (or equivalent for primary agent), use:
```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": ".praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": ".praxis-os"
    }
  }
}
```

**Important**: Primary agents **always** use `--transport dual` (enables HTTP for secondary agents).

Secondary agents then connect to the HTTP endpoint via URL (port allocated dynamically, written to `.praxis-os/.mcp_server_state.json`).

See specific secondary agent guides for detailed configuration.

## Common Questions

### Can I use multiple primary agents?

No - only one agent should control the MCP server. Use **primary + secondary** pattern instead.

### Can I switch between agents?

Yes, but only one primary agent at a time. Close the primary agent before starting another, or use secondary mode.

### Do I need different .cursorrules for different agents?

No - `.cursorrules` is agent-agnostic. The behavioral patterns work for any LLM-based agent.

### What if my agent isn't listed?

If your agent supports MCP protocol:
1. Follow the closest guide (probably Cline in VS Code or Cursor)
2. Adapt MCP configuration for your agent's format
3. Core concept: Point agent to `.praxis-os/venv/bin/python -m mcp_server`

### Can GitHub Copilot use prAxIs OS?

GitHub Copilot doesn't support MCP protocol (as of 2025). Consider using Cline or Claude Code in VS Code instead.

## Next Steps

1. **Choose your agent** - Primary or secondary mode
2. **Follow the guide** - Complete configuration for your agent
3. **Run orientation** - Start with 10 bootstrap queries
4. **Start building** - prAxIs OS provides guidance at every step

## Getting Help

- **Installation issues**: Check troubleshooting in your specific agent guide
- **MCP server issues**: See [MCP Server Update Guide](../../reference/mcp-tools.md)
- **Workflow questions**: See [Understanding Workflows](../../tutorials/understanding-praxis-os-workflows.md)

