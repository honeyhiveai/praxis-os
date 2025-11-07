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

## Step 1: Handle .cursorrules File

The `.cursorrules` file triggers prAxIs OS behavioral patterns. **⚠️ CRITICAL: Never blindly overwrite existing `.cursorrules` files!**

### Check for Existing File

```python
import os
import shutil
from datetime import datetime

if not os.path.exists(".cursorrules"):
    print("✅ No existing .cursorrules - safe to copy directly")
    # Copy from source
    shutil.copy("/path/to/praxis-os-source/.cursorrules", ".cursorrules")
    print("✅ .cursorrules installed")
else:
    print("⚠️  Existing .cursorrules detected!")
    print("   Cannot blindly overwrite - must handle safely")
    # Continue to merge protocol below
```

### Merge Protocol (If File Exists)

**⚠️ Never destroy user's existing configuration!**

#### Step 1: Read Both Files

```python
# Read existing rules
with open(".cursorrules", "r") as f:
    existing_rules = f.read()

# Read prAxIs OS rules
with open("/path/to/praxis-os-source/.cursorrules", "r") as f:
    praxis_os_rules = f.read()

print(f"📄 Your existing rules: {len(existing_rules.splitlines())} lines")
print(f"📄 prAxIs OS rules: {len(praxis_os_rules.splitlines())} lines")
```

#### Step 2: Present Options to User

```python
print("""
⚠️  Your project has existing .cursorrules

prAxIs OS rules MUST be at the TOP of your .cursorrules file.

Why top placement matters:
1. **Technical (Cursor)**: Cursor processes rules sequentially - prAxIs OS behavioral triggers must run first
2. **Attention span (All agents)**: LLMs read files top-to-bottom. Instructions at the top have the best chance of being followed, ensuring the orientation hook point is triggered

Options:
1. [Recommended] Auto-merge: prAxIs OS rules at top, your rules below
2. Manual merge: Show both files, you merge them yourself
3. Backup and replace: Use prAxIs OS rules only (your rules backed up)

Which option? (1/2/3): """)

user_choice = input().strip()
```

#### Step 3: Execute User's Choice

**Option 1: Auto-Merge (Recommended)**

```python
if user_choice == "1":
    # Create merged content
    merged_content = f"""# prAxIs OS Rules
# (Added during prAxIs OS installation on {datetime.now().strftime('%Y-%m-%d')})

{praxis_os_rules}

# ============================================================================
# Existing Project Rules (preserved from original .cursorrules)
# ============================================================================

{existing_rules}
"""
    
    # Backup original
    shutil.copy(".cursorrules", ".cursorrules.backup")
    
    # Write merged file
    with open(".cursorrules", "w") as f:
        f.write(merged_content)
    
    print("✅ Rules merged successfully!")
    print("   Structure: prAxIs OS rules (top) + Your rules (below)")
    print("   Backup: .cursorrules.backup")
    print("   Note: Top placement ensures orientation hook point is triggered")
```

**Option 2: Manual Merge**

```python
elif user_choice == "2":
    # Save prAxIs OS rules to temp file for user reference
    with open(".cursorrules.praxis-os", "w") as f:
        f.write(praxis_os_rules)
    
    print("""
📄 Files for manual merge:

Your existing rules:  .cursorrules
prAxIs OS rules:       .cursorrules.praxis-os

Instructions:
1. Open both files
2. Copy prAxIs OS rules from .cursorrules.praxis-os
3. Paste at the TOP of .cursorrules (critical for attention span and hook point)
4. Ensure your existing rules remain below
5. Save .cursorrules
6. Delete .cursorrules.praxis-os when done

Press Enter when you've completed the manual merge...
    """)
    
    input()  # Wait for user
    print("✅ Manual merge completed")
```

**Option 3: Backup and Replace**

```python
else:  # Option 3 or invalid input
    # Backup with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f".cursorrules.backup.{timestamp}"
    
    shutil.copy(".cursorrules", backup_path)
    
    # Replace with prAxIs OS rules
    shutil.copy("/path/to/praxis-os-source/.cursorrules", ".cursorrules")
    
    print(f"✅ Original rules backed up to: {backup_path}")
    print("   prAxIs OS rules are now active")
    print("\n💡 To restore your rules:")
    print("   1. Copy your rules from the backup")
    print("   2. Append them below prAxIs OS rules in .cursorrules")
```

### Verify .cursorrules Configuration

```python
# Check file exists
if not os.path.exists(".cursorrules"):
    print("❌ .cursorrules missing!")
    exit(1)

# Check it has prAxIs OS content
with open(".cursorrules", "r") as f:
    content = f.read()

has_praxis_os = "prAxIs OS" in content or "MANDATORY FIRST ACTION" in content

if not has_praxis_os:
    print("⚠️  .cursorrules exists but doesn't contain prAxIs OS rules")
    print("   Verify prAxIs OS rules are present at the top")
else:
    print("✅ .cursorrules configured with prAxIs OS rules")
```

**What it does:**
- Enforces orientation (10 mandatory bootstrap queries)
- Triggers `pos_search_project()` before actions
- Prevents direct file reads of indexed content
- Enforces "query liberally" pattern (5-10 queries per task)

## Step 2: Create MCP Configuration

Create `.cursor/mcp.json` to connect Cursor to the prAxIs OS MCP server:

```json
{
  "mcpServers": {
    "project-name": {
      "command": "/absolute/path/to/project/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
        "--transport",
        "dual"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project/.praxis-os"
      },
      "autoApprove": [
        "pos_search_project",
        "pos_workflow",
        "pos_browser",
        "pos_filesystem",
        "get_server_info",
        "current_date"
      ]
    }
  }
}
```

**⚠️ CRITICAL Configuration Requirements:**

1. **Use absolute paths** - Cursor does **NOT** expand `&#36;{workspaceFolder}` variables in MCP configuration. You must use absolute paths for both `command` and `PYTHONPATH`.

2. **Replace placeholders:**
   - Replace `"project-name"` with your actual project name (e.g., `"python-sdk"`, `"my-api"`, `"frontend"`)
   - Replace `/absolute/path/to/project/` with your actual project path (e.g., `/Users/josh/src/github.com/honeyhiveai/python-sdk`)

3. **Do NOT use `cwd` setting** - It causes path resolution issues. Use absolute `PYTHONPATH` instead.

4. **Project-specific server name** - Use your project name (not generic `"praxis-os"`) to:
   - Reinforce it as THE authoritative source for this project
   - Prevent conflicts when working on multiple projects
   - Make it clear which project's MCP server is running

**Windows users**: 
- Use forward slashes or double backslashes: `C:/Users/...` or `C:\\Users\\...`
- Change `venv/bin/python` to `venv\\Scripts\\python.exe`

**What this does:**
- Tells Cursor where to find the MCP server
- Points to the virtual environment Python using absolute path
- Sets PYTHONPATH to absolute path (no `cwd` needed)
- MCP server auto-starts when Cursor opens the project
- Auto-approves common tools for smoother workflow

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
"Run pos_search_project with query: orientation bootstrap"
```

**Expected output**: RAG results with orientation content

### Test 2: Verify Tool Availability

The following tools should be available (Cursor autocompletes them):
- `pos_search_project` - Semantic search over standards and code
- `pos_workflow` - Workflow management
- `pos_browser` - Browser automation (if needed)
- `pos_filesystem` - File operations
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
3. Never read indexed files (use pos_search_project)

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

# Test MCP server manually (use absolute path)
cd /path/to/project
PYTHONPATH=/path/to/project/.praxis-os .praxis-os/venv/bin/python -m ouroboros
```

**Solutions**:
- **Check configuration** - Ensure `mcp.json` uses absolute paths (not `&#36;{workspaceFolder}` or relative paths)
- **Check Cursor logs** - Look at `~/Library/Application Support/Cursor/logs/` for actual error messages
- Re-run: `python3 -m venv .praxis-os/venv`
- Re-install: `.praxis-os/venv/bin/pip install -r .praxis-os/ouroboros/requirements.txt`
- Check Python version: Must be 3.9+

### Tools Available But search_standards Returns Empty

**Symptom**: `pos_search_project` tool exists but returns no results

**Check**:
```bash
# Verify RAG index exists
ls -la .praxis-os/.cache/indexes/

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

### "Module not found: ouroboros"

**Symptom**: Python import error when MCP server starts (`ModuleNotFoundError: No module named ouroboros`)

**Check**:
```bash
# Verify ouroboros directory exists
ls -la .praxis-os/ouroboros/

# Check __main__.py exists
ls .praxis-os/ouroboros/__main__.py

# Test import manually (replace with your actual project path)
cd /path/to/project
PYTHONPATH=/path/to/project/.praxis-os .praxis-os/venv/bin/python -c "import ouroboros; print('✅ Success')"
```

**Solutions**:
- **Use absolute paths** - Ensure both `command` and `PYTHONPATH` in `mcp.json` use absolute paths (not relative or `&#36;{workspaceFolder}`)
- **Remove `cwd` setting** - It causes path resolution issues. Use absolute `PYTHONPATH` instead
- Re-run mechanical installation if ouroboros directory is missing
- Check Cursor logs at `~/Library/Application Support/Cursor/logs/` for actual errors

### "spawn workspaceFolder variable/... ENOENT"

**Symptom**: Cursor error: `spawn &#36;{workspaceFolder}/.praxis-os/venv/bin/python ENOENT`

**Root Cause**: Cursor does **NOT** expand `&#36;{workspaceFolder}` variables in MCP configuration. It tries to literally execute a command with that string.

**Solution**: 
- Replace all `&#36;{workspaceFolder}` references with absolute paths
- Use `/absolute/path/to/project/.praxis-os/venv/bin/python` instead of `&#36;{workspaceFolder}/.praxis-os/venv/bin/python`
- Use `/absolute/path/to/project/.praxis-os` for `PYTHONPATH` instead of `&#36;{workspaceFolder}/.praxis-os`

### RAG Index Slow or Incomplete

**Symptom**: First startup takes >30 seconds or searches miss content

**Check**:
```bash
# Count standards files
find .praxis-os/standards -name "*.md" | wc -l

# Check index size
du -sh .praxis-os/.cache/indexes/
```

**Expected**:
- ~60-80 standards files (universal + development)
- ~20-50MB index size
- 5-15 second initial build time

**Solutions**:
- Delete and rebuild: `rm -rf .praxis-os/.cache/indexes/`
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

