---
sidebar_position: 3
doc_type: how-to
---

# Claude Code (Terminal) Integration

Configure prAxIs OS to work with Claude Code CLI as your primary AI agent.

## Prerequisites

- ✅ Mechanical installation complete (via `install-praxis-os.py`)
- ✅ Claude Code installed (`npm install -g @anthropic-ai/claude-code` or similar)
- ✅ Anthropic API key configured
- ✅ `.praxis-os/` directory exists in your project

## Overview

Claude Code CLI is a standalone terminal-based AI coding assistant. As the **primary agent**, it will:
1. Control the MCP server lifecycle
2. Have full access to all prAxIs OS tools
3. Manage RAG index and workflows

You need:
1. `.cursorrules` file (behavioral triggers)
2. Claude Code MCP configuration
3. Start Claude Code in your project directory

## Step 1: Install Claude Code CLI

```bash
# Via npm (check official docs for latest)
npm install -g @anthropic-ai/claude-code

# Verify installation
claude-code --version
```

**Note**: Installation method may vary. Check [Anthropic's official docs](https://www.anthropic.com) for current CLI installation.

## Step 2: Configure API Key

```bash
# Set Anthropic API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Or add to shell profile (~/.zshrc, ~/.bashrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
```

## Step 3: Copy .cursorrules

```bash
# If .cursorrules doesn't exist
cp /path/to/praxis-os-source/.cursorrules .cursorrules

# .cursorrules affects LLM behavior via context
```

**What it does**:
- Triggers orientation (10 bootstrap queries)
- Enforces search-first protocol
- Prevents direct file reads of indexed content

## Step 4: Configure MCP for Claude Code

Claude Code uses a configuration file for MCP servers. Location varies by installation:

**Typical locations**:
- `~/.config/claude-code/mcp.json` (Linux/Mac)
- `~/.claude-code/mcp.json` (alternative)
- Project-level: `./.claude-code/mcp.json`

Create or edit the MCP configuration:

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": ".praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": "${workspaceFolder}/.praxis-os",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**Important**: Primary agents always use `--transport dual` to enable HTTP endpoint for secondary agents.

**Or use absolute paths**:
```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "/absolute/path/to/project/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": "/absolute/path/to/project/.praxis-os",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**Windows**: Change `venv/bin/python` to `venv\Scripts\python.exe`

## Step 5: Start Claude Code

```bash
# Navigate to your project
cd /path/to/your/project

# Start Claude Code
claude-code

# Or specify project directory
claude-code --project /path/to/project
```

On startup, Claude Code will:
1. Load MCP configuration
2. Start prAxIs OS MCP server
3. Connect to MCP server
4. Detect `.rebuild_index` flag → Build RAG index (first run)

**Expected startup**: 5-10 seconds for first RAG build

## Step 6: Validate Installation

### Test 1: Check MCP Connection

In Claude Code terminal:
```
"Use search_standards tool to query: orientation bootstrap"
```

**Expected**: RAG results with orientation content

### Test 2: List Available Tools

```
"What MCP tools are available?"
```

Should list:
- `search_standards`
- `pos_workflow`
- `pos_browser`
- `current_date`
- `get_server_info`

### Test 3: Test RAG Search

```
"Search prAxIs OS standards for concurrency patterns"
```

Should return relevant chunks from `.praxis-os/standards/`

## CLI Workflow Tips

### Running Orientation

```bash
# First thing in any session
> "Run the 10 mandatory orientation queries from .cursorrules"
```

Claude Code will read `.cursorrules` via context and execute queries.

### Creating Specs

```bash
> "Create a spec for user authentication feature"
```

Uses `pos_workflow` tool to start spec creation workflow.

### Querying Standards

```bash
> "How should I handle database connection pooling in Python?"
```

Uses `search_standards` to find relevant patterns.

### Running Workflows

```bash
> "Start the spec execution workflow for auth-feature spec"
```

Manages phase-gated workflow via `pos_workflow`.

## Troubleshooting

### MCP Server Won't Start

**Symptom**: "Failed to connect to MCP server" on Claude Code startup

**Check**:
```bash
# Test MCP server manually
cd .praxis-os
./venv/bin/python -m mcp_server
```

**Solutions**:
- Verify Python 3.9+ installed
- Check virtual environment exists: `ls .praxis-os/venv/`
- Re-install dependencies:
  ```bash
  .praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt
  ```
- Check MCP config path: `claude-code --show-config`

### Tools Unavailable

**Symptom**: Claude Code doesn't recognize `search_standards` or other tools

**Check**:
```bash
# Verify MCP config exists
cat ~/.config/claude-code/mcp.json
# or
cat ~/.claude-code/mcp.json
```

**Solutions**:
- Create MCP config file (Step 4)
- Use absolute paths instead of `${workspaceFolder}`
- Restart Claude Code after config changes
- Check Claude Code logs (if available)

### Empty Search Results

**Symptom**: `search_standards` returns no results

**Check**:
```bash
# Verify RAG index built
ls -la .praxis-os/.cache/vector_index/

# Check standards exist
find .praxis-os/standards -name "*.md" | wc -l
# Should be 60-80 files
```

**Solutions**:
- Create rebuild flag: `touch .praxis-os/standards/.rebuild_index`
- Restart Claude Code → Rebuilds index
- Verify permissions: `chmod -R u+rw .praxis-os/.cache/`

### Slow Performance

**Symptom**: Queries take >5 seconds

**Check**:
```bash
# Check system resources
top

# Check index size
du -sh .praxis-os/.cache/vector_index/
```

**Expected**:
- <1 second per query
- 20-50MB index size

**Solutions**:
- Rebuild index (delete `.praxis-os/.cache/vector_index/`)
- Ensure SSD (not HDD) for project
- Check Python not competing for CPU with other processes

### API Rate Limits

**Symptom**: "Rate limit exceeded" errors

**Note**: prAxIs OS tools run locally and don't call Anthropic API. But Claude Code LLM calls do.

**Solutions**:
- Wait for rate limit reset
- Upgrade Anthropic API tier
- Reduce query frequency (though prAxIs OS queries don't count toward API limits)

## Terminal vs VS Code Mode

Claude Code has two primary modes:

### Terminal (This Guide)
- ✅ Lightweight, fast startup
- ✅ Works in any terminal (tmux, screen, etc.)
- ✅ Good for server/remote development
- ❌ No GUI/editor integration

### VS Code Mode (See claude-code-vscode.md)
- ✅ Editor integration
- ✅ Visual diff, inline suggestions
- ✅ File tree, debugging
- ❌ Heavier, requires VS Code

Choose based on your workflow. Both support prAxIs OS equally.

## Configuration: Project vs Global

### Project-Level (Recommended)

```bash
# Create project-specific config
mkdir -p .claude-code
cat > .claude-code/mcp.json << 'EOF'
{
  "mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": "${workspaceFolder}/.praxis-os"
    }
  }
}
EOF
```

**Pros**: Team can share config, version controlled

### Global (Alternative)

```bash
# User-level config
mkdir -p ~/.config/claude-code
cat > ~/.config/claude-code/mcp.json << 'EOF'
{
  "mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": "${workspaceFolder}/.praxis-os"
    }
  }
}
EOF
```

**Pros**: Works for all projects automatically

## Multi-Project Setup

If you work on multiple projects with prAxIs OS:

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "cwd": "${workspaceFolder}/.praxis-os"
    }
  }
}
```

The `${workspaceFolder}` variable resolves to current project directory automatically.

## Next Steps

✅ **Installation complete!**

Now:
1. **Run orientation**: "Run the 10 mandatory bootstrap queries"
2. **Test search**: "Query standards for [topic]"
3. **Create spec**: "Create a spec for [feature]"
4. **Build with guidance**: prAxIs OS provides context throughout

See also:
- [Claude Code in VS Code](./claude-code-vscode.md) - Editor integration
- [Creating Project Standards](../creating-project-standards.md)
- [Understanding Workflows](../../tutorials/understanding-praxis-os-workflows.md)

