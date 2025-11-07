---
sidebar_position: 1
doc_type: how-to
---

# Cursor IDE Integration

Configure prAxIs OS to work with Cursor IDE's native MCP support.

## Prerequisites

- ✅ Mechanical installation complete (via `install-praxis-os.py`)
- ✅ Cursor IDE installed (v0.40+ for MCP support)
- ✅ `.praxis-os/` directory exists in your project

## Overview

Cursor has **native MCP support**, making it the simplest integration. You need:
1. `.cursorrules` file (behavioral triggers)
2. `.cursor/mcp.json` (MCP server configuration)
3. Restart Cursor to load MCP server

## Step 1: Copy .cursorrules

The `.cursorrules` file triggers prAxIs OS behavioral patterns.

```bash
# If .cursorrules doesn't exist
cp /path/to/praxis-os-source/.cursorrules .cursorrules

# If .cursorrules already exists
# See: "Merging Existing Rules" section below
```

**What it does:**
- Enforces orientation (10 mandatory bootstrap queries)
- Triggers `search_standards()` before actions
- Prevents direct file reads of indexed content
- Enforces "query liberally" pattern (5-10 queries per task)

## Step 2: Create MCP Configuration

Create `.cursor/mcp.json` to connect Cursor to the prAxIs OS MCP server:

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
      "cwd": ".praxis-os",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**Important**: Primary agents always use `--transport dual` to enable HTTP endpoint for secondary agents.

**Windows users**: Change `venv/bin/python` to `venv\Scripts\python.exe`

**What this does:**
- Tells Cursor where to find the MCP server
- Points to the virtual environment Python
- Sets working directory to `.praxis-os/`
- MCP server auto-starts when Cursor opens the project

## Step 3: Restart Cursor

```bash
# Close and reopen Cursor
# Or: Cmd+Q (Mac) / Alt+F4 (Windows), then reopen
```

On restart, Cursor will:
1. Read `.cursorrules` → Loads behavioral patterns
2. Parse `.cursor/mcp.json` → Starts MCP server
3. Connect to MCP server → Tools become available
4. Detect `.rebuild_index` flag → Builds RAG index automatically

**Expected startup time**: 5-10 seconds for first RAG index build

## Step 4: Validate Installation

Test that MCP tools are available:

### Test 1: Check MCP Connection

In Cursor chat, say:
```
"Run search_standards with query: orientation bootstrap"
```

**Expected output**: RAG results with orientation content

### Test 2: Verify Tool Availability

The following tools should be available (Cursor autocompletes them):
- `search_standards` - Semantic search over standards
- `pos_workflow` - Workflow management
- `pos_browser` - Browser automation (if needed)
- `current_date` - Get current date/time
- `get_server_info` - MCP server metadata

### Test 3: Check RAG Index

```
"Search for: python testing patterns"
```

Should return relevant chunks from `.praxis-os/standards/`

## Merging Existing .cursorrules

If you already have a `.cursorrules` file:

### Option A: Merge Manually (Recommended)

```bash
# Backup existing rules
cp .cursorrules .cursorrules.backup

# View both files
cat .cursorrules.backup
cat /path/to/praxis-os-source/.cursorrules

# Merge manually - keep your rules, add prAxIs OS rules
```

**Key sections to add from prAxIs OS:**
1. Orientation section (mandatory bootstrap queries)
2. Search-first protocol (query before acting)
3. Never read indexed files (use search_standards)

### Option B: Append (Simple)

```bash
# Add prAxIs OS rules to end of existing file
cat /path/to/praxis-os-source/.cursorrules >> .cursorrules
```

**Note**: This may create redundancy if rules overlap.

### Option C: Replace (Fresh Start)

```bash
# Use only prAxIs OS rules
cp .cursorrules .cursorrules.backup
cp /path/to/praxis-os-source/.cursorrules .cursorrules
```

## Troubleshooting

### MCP Server Won't Start

**Symptom**: Tools not available in Cursor chat

**Check**:
```bash
# Verify virtual environment exists
ls -la .praxis-os/venv/

# Test MCP server manually
.praxis-os/venv/bin/python -m mcp_server
```

**Solutions**:
- Re-run: `python3 -m venv .praxis-os/venv`
- Re-install: `.praxis-os/venv/bin/pip install -r .praxis-os/mcp_server/requirements.txt`
- Check Python version: Must be 3.9+

### Tools Available But search_standards Returns Empty

**Symptom**: `search_standards` tool exists but returns no results

**Check**:
```bash
# Verify RAG index exists
ls -la .praxis-os/.cache/vector_index/

# Check for rebuild flag (should be gone after first start)
ls .praxis-os/standards/.rebuild_index
```

**Solutions**:
- Create rebuild flag: `touch .praxis-os/standards/.rebuild_index`
- Restart Cursor → Index rebuilds automatically
- Verify standards exist: `ls .praxis-os/standards/universal/`

### Agent Ignores .cursorrules

**Symptom**: Agent doesn't run orientation queries or query liberally

**Check**:
```bash
# Verify .cursorrules in project root
ls -la .cursorrules

# Check file size (should be ~2KB with prAxIs OS rules)
wc -l .cursorrules
```

**Solutions**:
- Ensure `.cursorrules` is in project root (not `.praxis-os/`)
- Restart Cursor (rules load on startup)
- Explicitly trigger: "Run the 10 mandatory orientation queries"

### "Module not found: mcp_server"

**Symptom**: Python import error when MCP server starts

**Check**:
```bash
# Verify mcp_server directory exists
ls -la .praxis-os/mcp_server/

# Check __main__.py exists
ls .praxis-os/mcp_server/__main__.py
```

**Solutions**:
- Re-run mechanical installation
- Verify cwd in mcp.json is `.praxis-os`
- Check PYTHONPATH in mcp.json includes current directory

### RAG Index Slow or Incomplete

**Symptom**: First startup takes >30 seconds or searches miss content

**Check**:
```bash
# Count standards files
find .praxis-os/standards -name "*.md" | wc -l

# Check index size
du -sh .praxis-os/.cache/vector_index/
```

**Expected**:
- ~60-80 standards files (universal + development)
- ~20-50MB index size
- 5-15 second initial build time

**Solutions**:
- Delete and rebuild: `rm -rf .praxis-os/.cache/vector_index/`
- Create flag: `touch .praxis-os/standards/.rebuild_index`
- Restart Cursor → Rebuilds from scratch

## Primary vs Secondary Access Patterns

Cursor supports **primary MCP access** (native protocol):

### Primary (What You're Using)
- Direct MCP protocol via `.cursor/mcp.json`
- Native tool calling
- Full feature set
- Best performance

### Secondary (Fallback - Not Needed for Cursor)
- STDIO mode (if native MCP unavailable)
- HTTP mode (for remote servers)
- Not necessary for Cursor - it has native MCP

**Cursor users**: You're always using primary access. No fallback needed.

## LLM Component Selection

Cursor supports multiple LLM backends:

### Recommended for prAxIs OS
- **Claude 3.5 Sonnet** (default, best performance)
- **GPT-4 Turbo** (good alternative)

### Configuration
Cursor handles LLM selection via its UI settings. prAxIs OS works with any LLM Cursor supports - no special configuration needed.

**Note**: Tool calling quality varies by model. Claude 3.5 Sonnet has best MCP tool support.

## Next Steps

✅ **Installation complete!** 

Now try:
1. **Run orientation**: Start any chat with orientation queries (automatic via `.cursorrules`)
2. **Create a spec**: `"Create a spec for [feature]"` - Uses `pos_workflow` tool
3. **Query standards**: `"How should I handle [problem]?"` - Uses `search_standards`
4. **Build with guidance**: prAxIs OS provides context at every decision point

See also:
- [Creating Your First Standard](../../creating-project-standards.md)
- [Understanding Workflows](../../../tutorials/understanding-praxis-os-workflows.md)
- [Upgrading prAxIs OS](../../upgrading.md)

