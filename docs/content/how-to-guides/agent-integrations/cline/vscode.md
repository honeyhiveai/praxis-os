---
sidebar_position: 2
doc_type: how-to
---

# Cline in VS Code Integration (Primary)

Configure prAxIs OS to work with Cline extension in VS Code as your primary AI agent.

## Prerequisites

- ✅ Mechanical installation complete (via `install-praxis-os.py`)
- ✅ VS Code installed
- ✅ Cline extension installed from VS Code marketplace
- ✅ `.praxis-os/` directory exists in your project

## Overview

Cline is a VS Code extension that supports MCP. As the **primary agent**, Cline will:
1. Control the MCP server lifecycle (start/stop)
2. Have full access to all prAxIs OS tools
3. Manage the RAG index and workflows

You need:
1. `.cursorrules` file (behavioral triggers - yes, even for VS Code!)
2. Cline MCP configuration (via VS Code settings or Cline's UI)
3. Reload VS Code window to activate

## Step 1: Install Cline Extension

```bash
# Via VS Code marketplace
code --install-extension saoudrizwan.claude-dev

# Or: Search "Cline" in VS Code Extensions panel (Cmd+Shift+X)
```

**Verify installation**: Cline icon should appear in VS Code sidebar

## Step 2: Copy .cursorrules

The `.cursorrules` file works across all agents (Cursor, Cline, Claude Code, etc.):

```bash
# If .cursorrules doesn't exist
cp /path/to/praxis-os-source/.cursorrules .cursorrules

# If .cursorrules already exists
# See "Merging Existing Rules" in cursor.md guide
```

**Note**: Even though Cline is in VS Code, `.cursorrules` still affects LLM behavior through context.

## Step 3: Configure Cline for MCP

Cline supports two methods for MCP configuration:

### Method A: VS Code Settings (Recommended)

Open VS Code settings (`Cmd+,` or `Ctrl+,`), then:

1. Search for "Cline MCP"
2. Edit `settings.json` directly (click "Edit in settings.json")
3. Add prAxIs OS MCP server configuration:

```json
{
  "cline.mcpServers": {
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

**Windows users**: Change `venv/bin/python` to `venv\\Scripts\\python.exe`

### Method B: Cline UI (Alternative)

1. Open Cline sidebar
2. Click settings/gear icon
3. Navigate to "MCP Servers" section
4. Add server with:
   - **Name**: `praxis-os`
   - **Command**: `.praxis-os/venv/bin/python`
   - **Args**: `-m mcp_server --transport dual`
   - **Working Dir**: `.praxis-os`

**Important**: Primary agents always use `--transport dual` to enable HTTP endpoint for secondary agents.

## Step 4: Reload VS Code Window

```bash
# Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
> Developer: Reload Window

# Or restart VS Code completely
```

On reload, Cline will:
1. Read `.cursorrules` via context
2. Start prAxIs OS MCP server
3. Connect to MCP server
4. Detect `.rebuild_index` flag → Build RAG index

**Expected startup**: 5-10 seconds for first RAG index build

## Step 5: Validate Installation

### Test 1: Check MCP Connection

Open Cline and say:
```
"Use search_standards to query: orientation bootstrap"
```

**Expected**: RAG search results with orientation content

### Test 2: Verify Tool Availability

In Cline's tool list (check Cline UI), you should see:
- `search_standards` - Semantic search
- `pos_workflow` - Workflow management  
- `pos_browser` - Browser automation
- `current_date` - Date/time
- `get_server_info` - Server metadata

### Test 3: Check RAG Index

```
"Search prAxIs OS standards for python testing patterns"
```

Should return relevant chunks from `.praxis-os/standards/`

## Troubleshooting

### MCP Server Won't Start

**Symptom**: Cline shows "MCP server failed to start" or tools unavailable

**Check**:
```bash
# Verify virtual environment
ls -la .praxis-os/venv/

# Test MCP server manually
.praxis-os/venv/bin/python -m mcp_server
```

**Solutions**:
- Check Cline output panel (View → Output → select "Cline" dropdown)
- Verify Python path in settings: Use absolute path if `${workspaceFolder}` doesn't work
- Re-create venv: `python3 -m venv .praxis-os/venv`
- Re-install deps: `.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt`

### Tools Available But No Results

**Symptom**: `search_standards` exists but returns empty or errors

**Check**:
```bash
# Verify RAG index built
ls -la .praxis-os/.cache/vector_index/

# Check rebuild flag (should be gone after first start)
ls .praxis-os/standards/.rebuild_index
```

**Solutions**:
- Create rebuild flag: `touch .praxis-os/standards/.rebuild_index`
- Reload VS Code window → Index rebuilds
- Check Cline output panel for indexing errors

### Cline Doesn't Follow .cursorrules

**Symptom**: Cline doesn't run orientation or query liberally

**Root cause**: `.cursorrules` is Cursor-specific. Cline doesn't automatically read it.

**Solutions**:

**Option 1: Include in every chat (manual)**
```
"Read .cursorrules and follow all patterns, especially the 10 mandatory orientation queries"
```

**Option 2: Cline custom instructions (better)**

In Cline settings, add custom instructions:
```
BEFORE starting any task:
1. Run search_standards("orientation bootstrap queries mandatory ten queries")
2. Follow the 10 bootstrap queries returned
3. Query liberally (5-10 times per task) using search_standards
4. Never read .praxis-os/standards/ files directly - always use search_standards
```

**Option 3: Workspace-level prompt (best)**

Create `.vscode/settings.json`:
```json
{
  "cline.systemPrompt": "MANDATORY: Before any task, run search_standards('orientation bootstrap'). Follow all 10 bootstrap queries. Query liberally (5-10 times per task). Never read indexed files directly."
}
```

### Python Module Not Found

**Symptom**: `ModuleNotFoundError: No module named 'mcp_server'`

**Check**:
```bash
# Verify mcp_server exists
ls -la .praxis-os/mcp_server/__main__.py

# Check working directory in settings
cat .vscode/settings.json | grep cwd
```

**Solutions**:
- Ensure `cwd` is set to `${workspaceFolder}/.praxis-os` in settings
- Verify `PYTHONPATH` is set to `.` in env
- Check absolute paths if variables don't work

### Performance: Slow Searches

**Symptom**: `search_standards` takes >5 seconds per query

**Check**:
```bash
# Check index size
du -sh .praxis-os/.cache/vector_index/

# Count standards
find .praxis-os/standards -name "*.md" | wc -l
```

**Expected**:
- 60-80 standards files
- 20-50MB index size
- Less than 1 second per query

**Solutions**:
- Rebuild index: Delete `.praxis-os/.cache/vector_index/`, reload window
- Check system resources (CPU, RAM)
- Verify SSD (not HDD) for `.praxis-os/`

## Multi-Agent Setup (Optional)

If you also use Cursor and want both agents:

1. **Cursor** (primary) - Controls MCP server
2. **Cline in Cursor** (secondary) - Connects via HTTP

See [Cline in Cursor](./cursor.md) for secondary agent configuration.

**Note**: Don't run Cline (primary) and Cursor simultaneously - they'll conflict over MCP server.

## LLM Model Selection

Cline supports multiple models. Configure in Cline settings:

### Recommended for prAxIs OS
- **Claude 3.5 Sonnet** - Best MCP tool support
- **GPT-4 Turbo** - Good alternative
- **Claude 3 Opus** - Supported

### Configuration
1. Open Cline settings (gear icon)
2. Select "API Provider" (Anthropic, OpenAI, etc.)
3. Add API key
4. Select model

prAxIs OS works with any model Cline supports, but tool calling quality varies.

## VS Code Workspace Settings

For team consistency, commit `.vscode/settings.json` with Cline MCP config:

```json
{
  "cline.mcpServers": {
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
  "cline.systemPrompt": "MANDATORY: Run 10 orientation queries via search_standards before starting. Query liberally (5-10 times per task)."
}
```

**Add to `.gitignore`**: API keys in Cline settings (user-level, not workspace)

## Next Steps

✅ **Installation complete!**

Now:
1. **Run orientation**: Say "Run the 10 mandatory orientation queries"
2. **Test search**: "Query prAxIs OS standards for [topic]"
3. **Create spec**: "Create a spec for [feature]"
4. **Build with guidance**: prAxIs OS provides context throughout

See also:
- [Cline in Cursor](./cursor.md) - If using both Cursor + Cline

