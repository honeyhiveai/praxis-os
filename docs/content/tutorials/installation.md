---
sidebar_position: 2
doc_type: tutorial
---

# Installation

Install prAxIs OS in any project with a simple conversation. Your AI agent handles everything automatically.

## Quick Start

```bash
# In your IDE/agent, say:
"Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> (optional: in <IDE>)"

# Examples:
# "for Cursor"                    → Cursor IDE
# "for Cline in VS Code"          → Cline extension
# "for Claude Code"               → CLI/terminal mode
# "for Claude Code in VS Code"    → VS Code extension
# "for GitHub Copilot"            → GitHub Copilot
```

Your agent will:
1. **Run installation script** - Mechanical file operations (clone, copy, venv)
2. **Parse agent/IDE from command** - Routes to correct agent-specific guide
3. **Copy universal standards** - Timeless CS fundamentals
4. **Install MCP server** - Local Python process (Ouroboros)
5. **Configure your agent** - Agent-specific MCP integration files
6. **Build RAG index** - Auto-built by Ouroboros on server start

**Time:** ~5 minutes for complete installation

**📖 Need agent-specific setup?** See [Agent Integrations](../how-to-guides/agent-integrations/README.md) for detailed guides for Cursor, Cline, Claude Code, and more.

## What Gets Installed

```
your-project/
├── [agent-specific behavioral file]  # .cursorrules, .clinerules, .claude/CLAUDE.md, etc.
├── .praxis-os/
│   ├── standards/
│   │   ├── universal/            # Copied from repo
│   │   │   ├── concurrency/      # Race conditions, deadlocks, etc.
│   │   │   ├── architecture/     # SOLID, DI, API design
│   │   │   ├── testing/          # Test pyramid, test doubles
│   │   │   ├── failure-modes/    # Circuit breakers, retries
│   │   │   └── security/         # Security patterns
│   │   └── development/          # Generated for your language
│   │       ├── python-concurrency.md  # (if Python project)
│   │       ├── python-testing.md
│   │       └── python-architecture.md
│   ├── usage/                    # How to use prAxIs OS
│   ├── workflows/                # Phase-gated workflows
│   │   ├── spec_creation_v1/
│   │   └── spec_execution_v1/
│   ├── ouroboros/                # MCP/RAG server (copied)
│   │   ├── __main__.py
│   │   ├── subsystems/
│   │   ├── tools/
│   │   └── requirements.txt
│   ├── .cache/                   # Not tracked in git
│   │   └── indexes/              # RAG indexes (auto-built)
│   │       ├── standards/         # Standards vector index
│   │       └── code/             # Code vector + graph index
│   └── venv/                     # MCP server virtualenv
└── [agent-specific MCP config]   # .cursor/mcp.json, .vscode/settings.json, etc.
```

## Installation Steps (Detailed)

### 1. Mechanical Installation (Automated Script)

The installation script handles mechanical operations:

```bash
# Script automatically:
- Clones repository to temp directory
- Creates .praxis-os/ directory structure
- Copies standards, workflows, MCP server
- Creates Python venv and installs dependencies
- Configures .gitignore
- Cleans up temp files
```

**Time:** 2-3 minutes

### 2. Copy Universal Standards

```bash
# From repo → your project
cp -r praxis-os/universal/standards/ .praxis-os/standards/universal/
cp -r praxis-os/universal/usage/ .praxis-os/usage/
cp -r praxis-os/universal/workflows/ .praxis-os/workflows/
```

**What's copied:**
- Concurrency patterns (race conditions, deadlocks, locking)
- Architecture patterns (SOLID, DI, separation of concerns)
- Testing strategies (test pyramid, test doubles)
- Failure modes (circuit breakers, retry strategies)
- Security patterns
- Database patterns

### 3. Generate Language-Specific Standards

Your AI agent generates standards for your specific language:

**Python project example:**
```bash
# Your AI agent generates:
.praxis-os/standards/development/
├── python-concurrency.md        # GIL, threading, asyncio
├── python-testing.md            # pytest, unittest, coverage
├── python-architecture.md       # FastAPI/Django patterns
├── python-error-handling.md     # try/except, logging
└── python-code-quality.md       # mypy, black, ruff
```

**Content:**
- References universal standards
- Adds Python-specific implementations
- Includes your actual frameworks (FastAPI, Django, etc.)
- Your actual tools (pytest, mypy, black)
- Project-specific patterns found in your code

### 4. Install MCP Server

```bash
# Copy MCP server code
cp -r praxis-os/dist/ouroboros/ .praxis-os/ouroboros/

# Create virtualenv
cd .praxis-os
python -m venv venv

# Install dependencies
./venv/bin/pip install -r ouroboros/requirements.txt
```

**Dependencies installed:**
```
lancedb~=0.25.0              # Vector database
sentence-transformers>=2.0.0  # Local embeddings
mcp>=1.0.0                    # Model Context Protocol
watchdog>=3.0.0               # File watching
```

### 5. Customize Configuration

**⚠️ CRITICAL:** Before building the RAG index, customize `.praxis-os/config/mcp.yaml` to match your project's source code structure.

**Quick steps:**
1. Open `.praxis-os/config/mcp.yaml`
2. Update `code.source_paths` to point to your source directories (e.g., `["../src/"]`)
   - ✅ **Tip:** You can now point to top-level directories like `../src/` - prAxIs OS automatically respects your `.gitignore` file!
3. Update `code.languages` to list your languages (e.g., `["python", "typescript"]`)
4. Update `ast.source_paths` and `ast.languages` to match `code` settings

**✅ Automatic File Exclusion:**
- prAxIs OS automatically respects your project's `.gitignore` file (enabled by default)
- Build artifacts (`node_modules/`, `__pycache__/`, `dist/`, etc.) are automatically excluded
- No need to manually list excluded directories - it just works!
- See [Configuration Reference](../reference/config-reference) for advanced exclusion options

**📖 See [Configuration Reference](../reference/config-reference) for complete documentation and examples.**

**For detailed step-by-step instructions**: See [Manual Installation - Step 4](https://github.com/honeyhiveai/praxis-os/blob/main/installation/04-config-customization.md)

### 6. Configure Your Agent

After the mechanical installation completes, your agent parses the command to route to the correct agent-specific guide:

**Command Pattern:**
```
Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> (optional: in <IDE>)
```

**📖 See [Agent Integrations](../how-to-guides/agent-integrations/README.md) for complete setup guides:**
- **[Cursor](../how-to-guides/agent-integrations/cursor/)** - Native MCP support
- **[Cline in VS Code](../how-to-guides/agent-integrations/cline/vscode)** - VS Code extension
- **[Claude Code](../how-to-guides/agent-integrations/claude-code/vscode)** - VS Code integration
- **[Claude Code Terminal](../how-to-guides/agent-integrations/claude-code/terminal)** - CLI mode
- **[GitHub Copilot](../how-to-guides/agent-integrations/github-copilot/)** - GitHub Copilot

**Example: Cursor Configuration**

Create `.cursor/mcp.json` (Cursor-specific):

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
        "--transport",
        "dual",
        "--log-level",
        "INFO"
      ],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "pos_search_project",
        "pos_workflow",
        "get_server_info",
        "current_date"
      ]
    }
  }
}
```

**Transport Modes:**
- `dual`: stdio (IDE) + HTTP (enables secondary agents) - **Always used for primary agents**
- `stdio`: IDE communication only (not recommended - disables secondary agents)
- `http`: Network communication only (for testing or services)

**Why Primary Agents Use Dual Transport:**
- ✅ Primary agents (Cursor, Cline, Claude Code) **always** use `--transport dual`
- ✅ Enables HTTP endpoint for secondary agents to connect
- ✅ Primary agent uses stdio for its own connection (fast, native)
- ✅ Secondary agents connect via HTTP (no server launch needed)

**Restart your agent/IDE** to activate MCP server (agent-specific restart instructions in agent guides).

**Dual-Transport Benefits (standard for all primary agents):**
- ✅ IDE integration via stdio (primary agent's connection)
- ✅ HTTP endpoint automatically enabled (for secondary agents)
- ✅ Zero port conflicts (automatic port allocation 4242-5242 range)
- ✅ Multi-project support (each project gets its own port)
- ✅ Port written to `.praxis-os/.mcp_server_state.json` for secondary agents
- ✅ Secondary agents can connect anytime without reconfiguring primary

**Dynamic Port Allocation:**
- Server automatically finds available port in range 4242-5242
- Port written to `.praxis-os/.mcp_server_state.json` on startup
- Secondary agents read port from state file
- Helper scripts (`update-cline-mcp.py`) automatically configure secondary agents

### 6. Build RAG Index

First time the MCP server starts, it builds the vector index:

```python
# Auto-runs on first startup
Building RAG index...
- Scanning .praxis-os/standards/
- Scanning .praxis-os/workflows/
- Chunking markdown files
- Generating embeddings
- Building vector index

Index built in 58s
- 450 chunks indexed
- Ready for queries
```

**After first build:**
- File watcher monitors changes
- Auto-rebuilds index when files change
- No manual rebuilds needed

## Verify Installation

### Check MCP Server

```bash
# In your agent, say:
"Search standards for race conditions"
```

Should return relevant chunks from universal/development standards.

### Check Dual-Transport (standard for primary agents)

```bash
# Check state file (created automatically on startup with dual transport)
cat .praxis-os/.mcp_server_state.json

# Should show:
# - transport: "dual"
# - port: 4242 (or another available port in 4242-5242 range)
# - url: "http://127.0.0.1:4242/mcp" (or different port)
# - project info

# Test HTTP endpoint (for secondary agents)
PORT=$(cat .praxis-os/.mcp_server_state.json | grep -o '"port": [0-9]*' | grep -o '[0-9]*')
curl http://127.0.0.1:${PORT}/mcp  # Use port from state file
# Should return MCP server response

# In your agent, say:
"Call get_server_info tool"

# Should show server info including transport mode (dual)
```

### Check Workflows

```bash
# In your agent, say:
"Start spec creation workflow for user authentication"
```

Should initialize workflow and show Phase 0.

### Check Standards

```bash
# Check files were copied
ls -la .praxis-os/standards/universal/concurrency/
# Should see: race-conditions.md, deadlocks.md, etc.

ls -la .praxis-os/standards/development/
# Should see language-specific files
```

## Updating prAxIs OS

When new versions are released, use the upgrade workflow:

```bash
# In your agent, say:
"Run the prAxIs OS upgrade workflow"
```

The `praxis_os_upgrade_v1` workflow will:
1. ✅ Create automatic backup
2. ✅ Update standards, workflows, and MCP server
3. ✅ **Preserve your customizations** (specs, development standards)
4. ✅ Update `.gitignore` from standards
5. ✅ Validate everything works
6. ✅ Auto-rollback if anything fails

**Time:** ~3-4 minutes | **Safety:** Automatic backup and rollback

For detailed upgrade documentation, see **[Upgrading prAxIs OS](../how-to-guides/upgrading.md)**

## Manual Installation (Reference/Troubleshooting)

**Note**: The automated script is recommended. Use manual installation only for troubleshooting or understanding the process.

If you need manual control or want to understand each step:

```bash
# 1. Clone repo
git clone https://github.com/honeyhiveai/praxis-os.git

# 2. Copy to your project
cd your-project
cp -r praxis-os/universal .praxis-os/standards/universal
cp -r praxis-os/dist/ouroboros .praxis-os/ouroboros

# 3. Setup MCP server
cd .praxis-os
python -m venv venv
./venv/bin/pip install -r ouroboros/requirements.txt

# 4. Configure your agent
# See installation/03-agent-configuration.md to route to agent-specific guide
# Each agent has different MCP config file locations:
# - Cursor: .cursor/mcp.json
# - Cline: .vscode/settings.json (with cline.mcpServers key)
# - Claude Code: .vscode/settings.json (with claude-code.mcpServers key) or .mcp.json (CLI)
# - GitHub Copilot: .vscode/mcp.json

# 5. Generate language-specific standards
# Use your AI agent or manual creation
```

## Troubleshooting

### MCP Server Not Starting

```bash
# Check logs (agent-specific locations):
# - Cursor: Settings → MCP logs
# - VS Code: Output panel → MCP logs
# - Claude Code CLI: Check terminal output

# Common issues:
- Python version < 3.9
- Missing dependencies
- Invalid MCP config (check agent-specific config file)
```

### RAG Index Not Building

```bash
# Manual rebuild
cd .praxis-os
./venv/bin/python -c "
from ouroboros.subsystems.rag.index_manager import IndexManager
engine = RAGEngine(project_root='.')
engine.build_index()
"
```

### No Language-Specific Standards

Your AI agent may not have generated them. Manually create:

```bash
# Python example
cp praxis-os/language-instructions/python.md .praxis-os/
# Follow instructions to generate standards
```

## Requirements

- **AI Agent**: Cursor, Cline, Claude Code, or any MCP-compatible agent
- **Python**: 3.9+ (for MCP server)
- **Disk space**: ~500MB (includes embeddings model)
- **Memory**: ~200MB (MCP server runtime)

## Next Steps

- **[Agent Integrations](../how-to-guides/agent-integrations/README.md)** - Complete setup guides for your specific agent
- **[Architecture](../explanation/architecture)** - Understand how it works
- **[Standards](../reference/standards)** - Browse universal standards
- **[Workflows](../reference/workflows)** - Start using workflows

