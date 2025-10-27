# GitHub Copilot Agent Mode Integration

**Date**: 2025-10-24  
**Status**: Draft - Working Document  
**Context**: Document GitHub Copilot integration details and agent-integrations folder structure

---

## 🎯 Purpose

Capture the research and design for integrating Agent OS Enhanced with GitHub Copilot's Agent Mode via MCP (Model Context Protocol).

---

## Research Findings: GitHub Copilot Agent Mode

### How It Works

**Agent Mode Capabilities:**
- Autonomously handles multi-step development tasks
- Analyzes codebases, proposes and applies edits
- Runs commands and responds to build/lint errors
- Operates iteratively until task completion
- **Generally available** (as of 2025)

**MCP Support: YES ✅**

GitHub Copilot Agent Mode supports MCP (Model Context Protocol), enabling integration with external tools and services.

### Default MCP Servers (Built-in)

1. **GitHub MCP Server** - Access to issues, PRs, repo data
2. **Playwright MCP Server** - Web page interactions, screenshots, testing

### Configuration Methods

**Method 1: Repository-level (GitHub.com)**
- Navigate to: Repo Settings → Copilot → Coding agent → MCP configuration
- Add JSON configuration for MCP servers

**Method 2: Editor-level (VS Code/Visual Studio)**
- Create `mcp.json` file in workspace or global settings
- Restart editor to load new MCP servers

---

## MCP Configuration for Agent OS Enhanced

### VS Code Configuration

**File location:** `.vscode/mcp.json` or workspace `mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
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

**Windows version:**
```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server", "--transport", "dual", "--log-level", "INFO"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Visual Studio Configuration

**File location:** Solution directory `mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      }
    }
  }
}
```

### Cursor Configuration (Reference)

**File location:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual", "--log-level", "INFO"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state",
        "get_server_info"
      ]
    }
  }
}
```

---

## Proposed: `installation/agent-integrations/` Folder

### Structure

```
installation/
├── 00-START.md              ← Universal (mentions agent options)
├── 01-directories.md         ← Universal
├── 02-copy-files.md          ← Universal
├── 03-cursorrules.md         ← Universal
├── 04-gitignore.md           ← Universal
├── 05-venv-mcp.md            ← Currently Cursor-specific
├── 06-validate.md            ← Universal
├── POST-SCRIPT-TASKS.md      ← NEW (for hybrid install)
├── README.md
├── SYSTEM-SUMMARY.md
└── agent-integrations/       ← NEW FOLDER
    ├── README.md             ← Overview of supported agents
    ├── cursor.md             ← Cursor integration guide
    ├── github-copilot.md     ← GitHub Copilot + VS Code
    ├── visual-studio.md      ← Visual Studio integration
    └── (future agents)
```

### `agent-integrations/README.md` (Proposed)

```markdown
# Agent OS Enhanced - AI Agent Integrations

**Which AI agent are you using?**

Agent OS Enhanced works with multiple AI coding assistants via the Model Context Protocol (MCP).

## Supported Agents

### ✅ Cursor (Fully Supported)
- **Guide:** [cursor.md](cursor.md)
- **Status:** Primary development platform, fully tested
- **Features:** All Agent OS tools, dual-transport mode, auto-approval

### ✅ GitHub Copilot (VS Code) (Fully Supported)
- **Guide:** [github-copilot.md](github-copilot.md)
- **Status:** Tested with Copilot Agent Mode
- **Features:** All Agent OS tools via MCP

### 🚧 Visual Studio (Experimental)
- **Guide:** [visual-studio.md](visual-studio.md)
- **Status:** Configuration documented, needs testing
- **Features:** All Agent OS tools via MCP

### 🔮 Future Support
- **Windsurf** - Community requested
- **Claude Desktop** - MCP native
- **Cline** - VS Code extension

## Quick Start

1. **Install Agent OS Enhanced** (follow main installation guide)
2. **Choose your agent** from the list above
3. **Follow agent-specific guide** for MCP configuration
4. **Restart your editor**
5. **Test with:** `search_standards("test patterns")`

## Prerequisites

All agents require:
- ✅ Agent OS Enhanced installed (steps 01-04 complete)
- ✅ Python venv created (step 05)
- ✅ MCP server dependencies installed
- ✅ RAG index built

Only the MCP configuration differs between agents.
```

### `agent-integrations/github-copilot.md` (Proposed Content)

```markdown
# GitHub Copilot Agent Mode Integration

**For:** GitHub Copilot in VS Code  
**Status:** Fully supported  
**Prerequisites:** Agent OS Enhanced installation complete (steps 01-05)

---

## What This Guide Covers

After Agent OS Enhanced mechanical installation is complete, this guide shows you how to configure GitHub Copilot to use Agent OS tools via MCP.

---

## Step 1: Verify Prerequisites

Before configuring Copilot:

```bash
# Verify installation
ls -la .praxis-os/
# Should see: standards/, workflows/, mcp_server/, venv/, .cache/

# Verify venv
.praxis-os/venv/bin/python --version
# Should see: Python 3.9+

# Verify MCP server
.praxis-os/venv/bin/python -m mcp_server --help
# Should see: MCP server help text
```

---

## Step 2: Create MCP Configuration

**For VS Code:**

Create `mcp.json` in your workspace root:

```json
{
  "mcpServers": {
    "agent-os-rag": {
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

**For Windows:**

Use `Scripts/python.exe` instead:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/Scripts/python.exe",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      }
    }
  }
}
```

---

## Step 3: Restart VS Code

After creating `mcp.json`:

1. **Save the file**
2. **Close VS Code completely**
3. **Reopen VS Code** in your project directory
4. **Wait 10-15 seconds** for MCP server to start

---

## Step 4: Verify Integration

Test that Copilot can access Agent OS tools:

**In Copilot chat:**
```
Can you search_standards for "test patterns"?
```

**Expected response:**
Copilot should invoke the `search_standards` MCP tool and return results about testing patterns from Agent OS standards.

**Alternative test:**
```
What workflows are available?
```

Should trigger workflow discovery via MCP tools.

---

## Step 5: Orientation

After integration verified, Copilot should run orientation:

**Ask Copilot:**
```
Run Agent OS orientation queries
```

Copilot should automatically run the 9 bootstrap queries and reply with "✅ Oriented. Ready."

---

## Available Tools

Once integrated, Copilot has access to:

### RAG Tools
- `search_standards` - Semantic search over Agent OS standards
- `current_date` - Get current date (prevents AI date errors)

### Workflow Tools
- `start_workflow` - Initialize phase-gated workflows
- `get_current_phase` - Get current phase requirements
- `complete_phase` - Submit evidence and advance
- `get_workflow_state` - Query complete workflow state

### Browser Tools (if playwright installed)
- `aos_browser` - Browser automation for testing

### Server Info
- `get_server_info` - Server and project metadata

---

## Troubleshooting

### Issue: "Unknown tool: search_standards"

**Cause:** MCP server not loaded

**Fix:**
1. Check `mcp.json` exists in workspace root
2. Restart VS Code
3. Check VS Code output panel for MCP errors
4. Verify Python path is correct

### Issue: "Module not found: mcp_server"

**Cause:** PYTHONPATH not set correctly

**Fix:**
```json
"env": {
  "PYTHONPATH": "${workspaceFolder}/.praxis-os"
}
```

Ensure `.praxis-os` path is relative to workspace folder.

### Issue: MCP server starts but tools don't work

**Cause:** Dependencies not installed

**Fix:**
```bash
.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt
```

---

## Differences from Cursor

| Feature | Cursor | GitHub Copilot |
|---------|--------|----------------|
| MCP Config Location | `.cursor/mcp.json` | `mcp.json` (root) |
| Auto-approval | Supported | Not supported |
| Dual transport | Supported | Supported |
| Workflow execution | Full support | Full support |

**Note:** GitHub Copilot may prompt for tool approval more frequently than Cursor due to lack of auto-approval feature.

---

## Next Steps

After integration complete:

1. ✅ **Test basic queries** - `search_standards("test patterns")`
2. ✅ **Run orientation** - 9 bootstrap queries
3. ✅ **Try a workflow** - `start_workflow("spec_creation_v1", "feature.md")`
4. ✅ **Build something** - Use three-phase pattern (discuss → spec → build)

---

## Support

**Issues:**
- GitHub Issues: https://github.com/honeyhiveai/praxis-os/issues
- Tag: `integration:copilot`

**Documentation:**
- Main docs: `docs/content/`
- Installation: `installation/`
- Standards: `.praxis-os/standards/`

---

**Status:** Fully supported  
**Last Updated:** 2025-10-24  
**Tested With:** GitHub Copilot Agent Mode (October 2025)
```

---

## Key Differences Between Agents

| Feature | Cursor | GitHub Copilot | Visual Studio |
|---------|--------|----------------|---------------|
| MCP Config Path | `.cursor/mcp.json` | `mcp.json` (root) | `mcp.json` (solution dir) |
| Python Path (Unix) | `.praxis-os/venv/bin/python` | Same | N/A |
| Python Path (Win) | `.praxis-os/venv/Scripts/python.exe` | Same | Same |
| Auto-approval | Yes | No | No |
| Transport Mode | dual | dual | dual |
| Tool Discovery | Automatic | Automatic | Automatic |

---

## Installation Flow Impact

### Current (Cursor-only)

```
00 → 01 → 02 → 03 → 04 → 05-cursor → 06
```

### Proposed (Multi-agent)

**Fast path with script:**
```
Script (30 sec): Clone, copy, validate
    ↓
LLM: Detect language, generate standards, create venv
    ↓
LLM: Read agent-integrations/{agent}.md
    ↓
LLM: Create agent-specific MCP config
    ↓
LLM: Build RAG index, validate
```

**Guided path (manual):**
```
00 → 01 → 02 → 03 → 04 → 05-venv → agent-integrations/{agent}.md → 06
```

---

## Action Items

- [ ] **Decision:** Approve agent-integrations folder structure
- [ ] **Create:** `installation/agent-integrations/README.md`
- [ ] **Create:** `installation/agent-integrations/cursor.md` (extract from 05-venv-mcp.md)
- [ ] **Create:** `installation/agent-integrations/github-copilot.md` (new)
- [ ] **Create:** `installation/agent-integrations/visual-studio.md` (new)
- [ ] **Test:** GitHub Copilot integration in real project
- [ ] **Test:** Visual Studio integration (if accessible)
- [ ] **Update:** Main README to mention multi-agent support
- [ ] **Update:** `installation/README.md` to reference agent-integrations/
- [ ] **Update:** `.cursorrules` to mention we're editor-agnostic (optional)

---

## Testing Plan

### GitHub Copilot (VS Code)

1. **Setup:**
   - Fresh project
   - Install Agent OS Enhanced
   - Create `mcp.json` for Copilot
   - Restart VS Code

2. **Test Cases:**
   - [ ] MCP server starts successfully
   - [ ] `search_standards("test patterns")` works
   - [ ] Orientation queries (all 9) complete
   - [ ] Workflow creation via `start_workflow`
   - [ ] Phase completion via `complete_phase`
   - [ ] Browser tools (if installed)

3. **Success Criteria:**
   - All MCP tools accessible
   - No errors in VS Code output
   - Copilot can execute workflows
   - Documentation is clear and complete

---

## Notes

- **MCP is editor-agnostic** - Same server works with all agents
- **Only config differs** - Python path, config location, transport mode
- **Dual transport enables sub-agents** - HTTP endpoint for multi-agent workflows
- **Agent OS tools are universal** - RAG, workflows, browser all work regardless of editor

---

**Status:** Working document - awaiting decision to implement  
**Next:** Get approval, then create formal guides in `installation/agent-integrations/`

