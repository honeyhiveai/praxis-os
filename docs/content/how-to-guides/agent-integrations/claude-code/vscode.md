---
sidebar_position: 2
doc_type: how-to
---

# Claude Code in VS Code Integration

Configure prAxIs OS to work with Claude Code extension in VS Code as your primary AI agent.

## Prerequisites

- ✅ Mechanical installation complete (via `install-praxis-os.py`)
- ✅ VS Code installed
- ✅ Claude Code extension installed
- ✅ Anthropic API key configured
- ✅ `.praxis-os/` directory exists

## Overview

Claude Code for VS Code is an editor-integrated AI assistant. As the **primary agent**, it will:
1. Control the MCP server lifecycle
2. Have full access to all prAxIs OS tools
3. Manage RAG index and workflows
4. Provide inline suggestions, diffs, and editor integration

You need:
1. `.cursorrules` file (behavioral triggers)
2. VS Code MCP configuration for Claude Code
3. Reload VS Code window

## Step 1: Install Claude Code Extension

```bash
# Via VS Code marketplace
code --install-extension anthropic.claude-code

# Or: Search "Claude Code" in VS Code Extensions (Cmd+Shift+X)
```

**Verify**: Claude Code icon should appear in VS Code sidebar

## Step 2: Configure API Key

1. Open Claude Code sidebar (click icon)
2. Click "Configure API Key"
3. Enter your Anthropic API key: `sk-ant-...`

**Or via environment**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Add to ~/.zshrc or ~/.bashrc for persistence
```

## Step 3: Copy .cursorrules

```bash
# If .cursorrules doesn't exist
cp /path/to/praxis-os-source/.cursorrules .cursorrules

# .cursorrules affects LLM behavior via context
```

**What it does**:
- Triggers orientation queries
- Enforces search-first protocol
- Prevents direct file reads of indexed content

## Step 4: Configure Claude Code for MCP

Edit VS Code workspace settings (`.vscode/settings.json`):

```json
{
  "claude-code.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
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

**Windows**: Change `venv/bin/python` to `venv\\Scripts\\python.exe`

**Note**: Property name may be `claude-code.mcpServers` or `claudeCode.mcpServers` - check Claude Code documentation for current version.

## Step 5: Reload VS Code Window

```bash
# Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
> Developer: Reload Window
```

On reload, Claude Code will:
1. Start prAxIs OS MCP server
2. Connect to MCP server
3. Detect `.rebuild_index` flag → Build RAG index
4. Load `.cursorrules` via context

**Expected startup**: 5-10 seconds for first RAG build

## Step 6: Validate Installation

### Test 1: Check MCP Connection

In Claude Code chat:
```
"Use search_standards to query: orientation bootstrap"
```

**Expected**: RAG results with orientation content

### Test 2: List Tools

Check Claude Code UI or ask:
```
"What MCP tools are available?"
```

Should see:
- `search_standards`
- `pos_workflow`
- `pos_browser`
- `current_date`
- `get_server_info`

### Test 3: Test RAG Search

```
"Search prAxIs OS standards for Python async patterns"
```

Should return relevant chunks from `.praxis-os/standards/`

## Editor Integration Features

Claude Code in VS Code provides additional features beyond terminal mode:

### Inline Suggestions

```python
# Claude Code can suggest completions using prAxIs OS context
def handle_concurrent_requests():
    # Type here, Claude suggests based on standards
```

### Diff View

```
"Refactor this function using prAxIs OS concurrency patterns"
```

Claude shows side-by-side diff with proposed changes.

### File Tree Integration

Claude Code can:
- Navigate project structure
- Create/modify multiple files
- Follow prAxIs OS project organization

### Terminal Integration

```
"Run tests and show results"
```

Claude executes commands and interprets output.

## Troubleshooting

### MCP Server Won't Start

**Symptom**: "MCP server connection failed" in Claude Code output

**Check**:
```bash
# Test MCP server manually
.praxis-os/venv/bin/python -m mcp_server

# Check VS Code Output panel
# View → Output → Select "Claude Code" from dropdown
```

**Solutions**:
- Verify Python 3.9+ installed
- Check venv exists: `ls .praxis-os/venv/`
- Re-install dependencies:
  ```bash
  .praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt
  ```
- Use absolute path if `${workspaceFolder}` doesn't resolve
- Check Claude Code documentation for current config format

### Tools Not Available

**Symptom**: Claude Code doesn't recognize `search_standards` or other tools

**Check**:
```bash
# Verify MCP config in settings
cat .vscode/settings.json | grep -A 10 mcp

# Check Claude Code output panel for errors
```

**Solutions**:
- Reload VS Code window after config changes
- Verify config property name (`claude-code.mcpServers` vs `claudeCode.mcpServers`)
- Check Claude Code extension version (may need update)
- Test with absolute paths instead of `${workspaceFolder}`

### Empty Search Results

**Symptom**: `search_standards` returns no results or errors

**Check**:
```bash
# Verify RAG index
ls -la .praxis-os/.cache/vector_index/

# Check standards exist
find .praxis-os/standards -name "*.md" | wc -l
# Should be 60-80 files
```

**Solutions**:
- Create rebuild flag: `touch .praxis-os/standards/.rebuild_index`
- Reload VS Code → Index rebuilds automatically
- Check Claude Code output for indexing errors
- Verify permissions: `chmod -R u+rw .praxis-os/.cache/`

### Claude Code Doesn't Follow .cursorrules

**Symptom**: Claude doesn't run orientation or query liberally

**Root cause**: `.cursorrules` is Cursor-specific

**Solutions**:

**Option 1: Custom instructions in Claude Code settings**

In Claude Code settings, add system prompt:
```
MANDATORY: Before any task, run search_standards("orientation bootstrap queries"). Follow all 10 queries. Query liberally (5-10 times per task). Never read indexed files directly.
```

**Option 2: Workspace settings**

In `.vscode/settings.json`:
```json
{
  "claude-code.systemPrompt": "MANDATORY: Run 10 orientation queries before starting. Query liberally. Use search_standards, never read .praxis-os files directly."
}
```

**Option 3: Mention in first message**

```
"Read .cursorrules and follow all patterns throughout this session"
```

### Slow Performance

**Symptom**: Searches take >5 seconds

**Check**:
```bash
# Index size
du -sh .praxis-os/.cache/vector_index/

# System resources
top
```

**Expected**:
- Less than 1 second per query
- 20-50MB index

**Solutions**:
- Rebuild index (delete cache, reload window)
- Ensure SSD (not HDD)
- Close other resource-intensive applications
- Check Python not bottlenecked

## VS Code vs Terminal Mode

| Aspect | VS Code (This Guide) | Terminal (CLI) |
|--------|----------------------|----------------|
| **Interface** | Editor-integrated | Command-line only |
| **Inline Suggestions** | ✅ Yes | ❌ No |
| **Diff View** | ✅ Visual side-by-side | ❌ Text only |
| **File Navigation** | ✅ Tree view | ❌ Manual |
| **Startup** | Slower (loads VS Code) | Faster (CLI only) |
| **Remote Dev** | ✅ Works via Remote-SSH | ✅ Works natively |
| **prAxIs OS Support** | ✅ Full MCP access | ✅ Full MCP access |

Both modes have identical prAxIs OS functionality - choose based on workflow preference.

## Multi-Agent Setup (Optional)

If using both Claude Code (VS Code) and Cursor:

**Option 1: One primary at a time**
- Use Claude Code OR Cursor, not simultaneously
- Both want to control MCP server → conflict

**Option 2: Claude Code primary, Cursor secondary**
- Not common pattern (Cursor usually primary)
- Requires HTTP mode in Claude Code (check if supported)

**Recommended**: Choose one primary agent per project.

## Workspace Settings for Team

Commit `.vscode/settings.json` for team consistency:

```json
{
  "claude-code.mcpServers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
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
  },
  "claude-code.systemPrompt": "MANDATORY: Run orientation queries before starting. Query liberally (5-10 times/task)."
}
```

**Don't commit**: API keys (user-level setting, not workspace)

## LLM Model Selection

Claude Code uses Claude models exclusively:

- **Claude 3.5 Sonnet** - Recommended, best MCP support
- **Claude 3 Opus** - More capable, slower
- **Claude 3 Haiku** - Faster, less capable

Configure in Claude Code settings (model selection dropdown).

## Next Steps

✅ **Installation complete!**

Now:
1. **Run orientation**: "Run the 10 mandatory orientation queries"
2. **Test search**: "Query standards for [topic]"
3. **Create spec**: "Create a spec for [feature]"
4. **Use editor features**: Inline suggestions, diff view, etc.

See also:
- [Claude Code Terminal](./terminal.md) - CLI mode
- [Creating Project Standards](../../creating-project-standards.md)
- [Understanding Workflows](../../../tutorials/understanding-praxis-os-workflows.md)

