---
sidebar_position: 3
doc_type: how-to
---

# GitHub Copilot Integration

Configure prAxIs OS to work with GitHub Copilot's MCP support across multiple IDEs.

## Prerequisites

- ✅ Mechanical installation complete (via `install-praxis-os.py`)
- ✅ GitHub Copilot extension installed in your IDE
- ✅ `.praxis-os/` directory exists in your project
- ✅ If you're in an organization/enterprise: "MCP servers in Copilot" policy must be enabled

## Supported IDEs

GitHub Copilot supports MCP in the following IDEs:

- **VS Code** (via GitHub Copilot extension)
- **JetBrains IDEs** (IntelliJ IDEA, PyCharm, WebStorm, CLion, GoLand, etc.)
- **Xcode** (via GitHub Copilot for Xcode extension)
- **Eclipse** (version 2024-09 or above)

## Overview

GitHub Copilot supports MCP protocol, allowing you to use prAxIs OS tools directly in Copilot Chat. As the **primary agent**, GitHub Copilot will:
1. Control the MCP server lifecycle (start/stop)
2. Have full access to all prAxIs OS tools
3. Manage the RAG index and workflows

You need:
1. `.github/copilot-instructions.md` file (behavioral triggers - GitHub Copilot's equivalent to `.cursorrules`)
2. MCP server configuration (`.vscode/mcp.json` for VS Code, or IDE-specific location)
3. Restart IDE/Copilot to load MCP server

## Step 1: Handle .github/copilot-instructions.md File

GitHub Copilot uses `.github/copilot-instructions.md` for repository-level custom instructions (similar to `.cursorrules` for Cursor). This file triggers prAxIs OS behavioral patterns. **⚠️ CRITICAL: Never blindly overwrite existing `.github/copilot-instructions.md` files!**

### Check for Existing File

```python
import os
import shutil
from datetime import datetime

# Ensure .github directory exists
os.makedirs(".github", exist_ok=True)

instructions_path = ".github/copilot-instructions.md"

if not os.path.exists(instructions_path):
    print("✅ No existing .github/copilot-instructions.md - safe to copy directly")
    # Copy from source repository
    source_file = "/path/to/praxis-os-source/.github/copilot-instructions.md"
    if os.path.exists(source_file):
        shutil.copy(source_file, instructions_path)
        print("✅ .github/copilot-instructions.md installed")
    else:
        # Fallback: Create from .cursorrules (same content)
        cursorrules_source = "/path/to/praxis-os-source/.cursorrules"
        if os.path.exists(cursorrules_source):
            shutil.copy(cursorrules_source, instructions_path)
            print("✅ Created .github/copilot-instructions.md from .cursorrules")
        else:
            print("⚠️  Source file not found - manual creation required")
else:
    print("⚠️  Existing .github/copilot-instructions.md detected!")
    print("   Cannot blindly overwrite - must handle safely")
    # Continue to merge protocol below
```

### Merge Protocol (If File Exists)

**⚠️ Never destroy user's existing configuration!**

#### Step 1: Read Both Files

```python
# Read existing instructions
with open(".github/copilot-instructions.md", "r") as f:
    existing_instructions = f.read()

# Read prAxIs OS rules (from .github/copilot-instructions.md or .cursorrules as fallback)
source_file = "/path/to/praxis-os-source/.github/copilot-instructions.md"
if not os.path.exists(source_file):
    # Fallback to .cursorrules (same content)
    source_file = "/path/to/praxis-os-source/.cursorrules"

with open(source_file, "r") as f:
    praxis_os_rules = f.read()

print(f"📄 Your existing instructions: {len(existing_instructions.splitlines())} lines")
print(f"📄 prAxIs OS rules: {len(praxis_os_rules.splitlines())} lines")
```

#### Step 2: Present Options to User

```python
print("""
⚠️  Your project has existing .github/copilot-instructions.md

prAxIs OS rules MUST be at the TOP of your copilot-instructions.md file.

Why top placement matters:
1. **Attention span**: LLMs read files sequentially - instructions at the top have the best chance of being followed
2. **Hook point**: Ensures orientation queries are triggered before other rules

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
    merged_content = f"""# prAxIs OS Instructions
# (Added during prAxIs OS installation on {datetime.now().strftime('%Y-%m-%d')})

{praxis_os_rules}

# ============================================================================
# Existing Project Instructions (preserved from original copilot-instructions.md)
# ============================================================================

{existing_instructions}
"""
    
    # Backup original
    shutil.copy(".github/copilot-instructions.md", ".github/copilot-instructions.md.backup")
    
    # Write merged file
    with open(".github/copilot-instructions.md", "w") as f:
        f.write(merged_content)
    
    print("✅ Instructions merged successfully!")
    print("   Structure: prAxIs OS rules (top) + Your rules (below)")
    print("   Backup: .github/copilot-instructions.md.backup")
    print("   Note: Top placement ensures orientation hook point is triggered")
```

**Option 2: Manual Merge**

```python
elif user_choice == "2":
    # Save prAxIs OS rules to temp file for user reference
    with open(".github/copilot-instructions.praxis-os", "w") as f:
        f.write(praxis_os_rules)
    
    print("""
📄 Files for manual merge:

Your existing instructions:  .github/copilot-instructions.md
prAxIs OS rules:              .github/copilot-instructions.praxis-os

Instructions:
1. Open both files
2. Copy prAxIs OS rules from .github/copilot-instructions.praxis-os
3. Paste at the TOP of .github/copilot-instructions.md (critical for attention span and hook point)
4. Ensure your existing instructions remain below
5. Save .github/copilot-instructions.md
6. Delete .github/copilot-instructions.praxis-os when done

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
    backup_path = f".github/copilot-instructions.md.backup.{timestamp}"
    
    shutil.copy(".github/copilot-instructions.md", backup_path)
    
    # Replace with prAxIs OS rules
    with open(".github/copilot-instructions.md", "w") as f:
        f.write(f"""# prAxIs OS Instructions
# (Added during prAxIs OS installation on {datetime.now().strftime('%Y-%m-%d')})

{praxis_os_rules}
""")
    
    print(f"✅ Original instructions backed up to: {backup_path}")
    print("   prAxIs OS rules are now active")
    print("\n💡 To restore your instructions:")
    print("   1. Copy your instructions from the backup")
    print("   2. Append them below prAxIs OS rules in .github/copilot-instructions.md")
```

### Verify .github/copilot-instructions.md Configuration

```python
# Check file exists
if not os.path.exists(".github/copilot-instructions.md"):
    print("❌ .github/copilot-instructions.md missing!")
    exit(1)

# Check it has prAxIs OS content
with open(".github/copilot-instructions.md", "r") as f:
    content = f.read()

has_praxis_os = "prAxIs OS" in content or "MANDATORY FIRST ACTION" in content

if not has_praxis_os:
    print("⚠️  .github/copilot-instructions.md exists but doesn't contain prAxIs OS rules")
    print("   Verify prAxIs OS rules are present at the top")
else:
    print("✅ .github/copilot-instructions.md configured with prAxIs OS rules")
```

**What it does:**
- Enforces orientation (10 mandatory bootstrap queries)
- Triggers `pos_search_project()` before actions
- Prevents direct file reads of indexed content
- Enforces "query liberally" pattern (5-10 queries per task)

**Note**: GitHub Copilot uses `.github/copilot-instructions.md` instead of `.cursorrules`. The content is similar, but the file location and name are GitHub Copilot-specific.

## Step 2: Configure MCP Server

GitHub Copilot supports two methods for configuring MCP servers:

### Method A: MCP Registry (Recommended - Easiest)

The MCP Registry allows you to browse and install MCP servers directly from Copilot Chat.

#### VS Code

1. In VS Code, open Copilot Chat
2. Click the **MCP icon** (🔧) in the chat window
3. In the MCP Registry window, search for or browse available servers
4. Find "prAxIs OS" (or configure manually if not in registry)
5. Click **Install** next to the server
6. Click **OK** to save
7. Click the **tools icon** in Copilot Chat - you should see prAxIs OS tools

#### JetBrains IDEs

1. In your JetBrains IDE, open Copilot Chat
2. Click the **MCP icon** (🔧) in the chat window
3. In the MCP Registry window, find the prAxIs OS server
4. Click **Install** next to the server
5. Click **OK** to save
6. Click the **tools icon** - you should see prAxIs OS tools

#### Xcode

1. In Xcode, open Copilot Chat
2. Click the **⚙️ icon** to open settings
3. Select the **Tools** tab
4. Next to **MCP Registry URL (Optional)**, click **Browse MCP Servers**
5. Find the prAxIs OS server and click **Install**
6. Close the MCP Servers Marketplace window
7. Under **Available MCP Tools**, expand the list to see prAxIs OS tools

#### Eclipse

1. In Eclipse, open Copilot Chat
2. Click the **MCP icon** (🔧) in the chat window
3. In the MCP Registry window, find the prAxIs OS server
4. Click **Install** next to the server
5. Click **Close** to save
6. Click the **tools icon** - you should see prAxIs OS tools

### Method B: Manual Configuration (Advanced)

If the MCP Registry doesn't work or you prefer manual configuration, edit `mcp.json` directly.

#### VS Code

1. Open Copilot Chat in VS Code
2. Click the **tools icon** (called "Configure your MCP server") at the bottom of the chat window
3. Click **Add MCP Tools**
4. This will create or edit `.vscode/mcp.json` in your project root

**Configuration location**: `.vscode/mcp.json` (project-specific, committed to repo)

**Create the file manually** if needed:
```bash
mkdir -p .vscode
```

**Example `.vscode/mcp.json`**:
```json
{
  "servers": {
    "praxis-os": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
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

**Windows**: Change `venv/bin/python` to `venv\\Scripts\\python.exe`

**Note**: `.vscode/mcp.json` is project-specific and should be committed to your repository so all team members share the same MCP configuration.

#### JetBrains IDEs

1. In the lower right corner, click **⚙️**
2. From the menu, select "Open Chat", make sure you're in **Agent mode**
3. Click the **tools icon** ("Configure your MCP server") at the bottom
4. Click **Add MCP Tools**
5. Edit the `mcp.json` file

**Example `mcp.json`**:
```json
{
  "servers": {
    "praxis-os": {
      "command": ".praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
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

**Windows**: Change `venv/bin/python` to `venv\\Scripts\\python.exe`

#### Xcode

1. Open GitHub Copilot for Xcode extension and go to **Settings**
   - Or: **Editor** → **GitHub Copilot** → **Open GitHub Copilot for Xcode Settings**
2. Select the **MCP** tab
3. Click **Edit Config**
4. Edit the `mcp.json` file

**Example `mcp.json`**:
```json
{
  "servers": {
    "praxis-os": {
      "command": ".praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
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

#### Eclipse

1. Click the **Copilot icon** (🤖) in the status bar at the bottom
2. Select **Open Chat** and click the **"Configure Tools..."** icon
   - Or: **Edit preferences** → **GitHub Copilot** → **MCP**
3. Under "Server Configurations", define your MCP servers

**Example configuration**:
```json
{
  "servers": {
    "praxis-os": {
      "command": ".praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
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

## Step 3: Verify Installation

### Test 1: Check MCP Connection

In Copilot Chat, ask:
```
"What MCP tools are available?"
```

**Expected**: Copilot should list prAxIs OS tools:
- `pos_search_project` - Search standards, code, AST
- `pos_workflow` - Workflow management
- `pos_browser` - Browser automation
- `pos_filesystem` - File operations
- `current_date` - Date/time utilities
- `get_server_info` - Server status

### Test 2: Test Search Standards

In Copilot Chat, ask:
```
"Search for: python testing patterns"
```

**Expected**: Should return relevant chunks from `.praxis-os/standards/`

### Test 3: Verify Server Status

In Copilot Chat, ask:
```
"Get prAxIs OS server status"
```

**Expected**: Should return server metadata, health status, and version information

## Troubleshooting

### MCP Server Won't Start

**Symptom**: Tools not available in Copilot Chat

**Check**:
```bash
# Verify virtual environment exists
ls -la .praxis-os/venv/

# Test MCP server manually
.praxis-os/venv/bin/python -m ouroboros
```

**Solutions**:
- Re-run: `python3 -m venv .praxis-os/venv`
- Re-install: `.praxis-os/venv/bin/pip install -r .praxis-os/ouroboros/requirements.txt`
- Check Python version: Must be 3.9+
- Verify `mcp.json` syntax is valid JSON

### Tools Available But search_standards Returns Empty

**Symptom**: `pos_search_project` tool exists but returns no results

**Check**:
```bash
# Verify RAG index exists
ls -la .praxis-os/.cache/vector_index/

# Check for rebuild flag (should be gone after first start)
ls .praxis-os/standards/.rebuild_index
```

**Solutions**:
- Create rebuild flag: `touch .praxis-os/standards/.rebuild_index`
- Restart IDE → Index rebuilds automatically
- Verify standards exist: `ls .praxis-os/standards/universal/`

### Copilot Doesn't Follow Instructions

**Symptom**: Agent doesn't run orientation queries or query liberally

**Check**:
```bash
# Verify .github/copilot-instructions.md in project root
ls -la .github/copilot-instructions.md

# Check file size (should be ~2KB with prAxIs OS rules)
wc -l .github/copilot-instructions.md
```

**Solutions**:
- Ensure `.github/copilot-instructions.md` is in project root (not `.praxis-os/`)
- Restart IDE (instructions load on startup)
- Explicitly trigger: "Run the 10 mandatory orientation queries"
- Verify prAxIs OS rules are at the TOP of the file

### "Module not found: ouroboros"

**Symptom**: Python import error when MCP server starts

**Check**:
```bash
# Verify ouroboros directory exists
ls -la .praxis-os/ouroboros/

# Check __main__.py exists
ls .praxis-os/ouroboros/__main__.py
```

**Solutions**:
- Re-run mechanical installation
- Verify `cwd` in `mcp.json` is `.praxis-os`
- Check `PYTHONPATH` in `mcp.json` includes current directory

### MCP Registry Not Showing prAxIs OS

**Symptom**: Can't find prAxIs OS in MCP Registry

**Solution**: Use manual configuration (Method B above). The MCP Registry may not include all servers, especially custom/local ones.

### Configuration File Location Unknown

**Symptom**: Can't find where `mcp.json` is stored

**Solutions**:
- **VS Code**: Configuration is in `.vscode/mcp.json` (project root)
- **JetBrains**: Look in IDE settings under GitHub Copilot → MCP
- **Xcode**: Settings → Tools tab → MCP section
- **Eclipse**: Preferences → GitHub Copilot → MCP

## IDE-Specific Notes

### VS Code

- MCP configuration is stored in `.vscode/mcp.json` (project-specific)
- This file should be committed to your repository for team consistency
- VS Code variables like `${workspaceFolder}` are supported in paths
- Property name in settings may vary: `github.copilot.mcpServers` or similar (check extension settings)

### JetBrains IDEs

- Configuration is IDE-specific (not shared across JetBrains IDEs)
- Each IDE (IntelliJ, PyCharm, etc.) has its own MCP configuration
- Configuration persists per IDE installation

### Xcode

- Requires GitHub Copilot for Xcode extension
- MCP configuration is stored in extension settings
- May require Xcode restart after configuration

### Eclipse

- Requires Eclipse 2024-09 or above
- MCP configuration is stored in Eclipse preferences
- May require Eclipse restart after configuration

## Next Steps

1. **Run orientation**: Start any chat with orientation queries (automatic via `.github/copilot-instructions.md`)
2. **Test tools**: Try `pos_search_project` to search standards
3. **Start workflows**: Use `pos_workflow` to manage phase-gated workflows
4. **Explore**: Use `pos_browser` for web automation, `pos_filesystem` for file operations

## Reference

- [GitHub Copilot MCP Documentation](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/extend-copilot-chat-with-mcp)
- [Cursor Integration Guide](../cursor/index.md) - Similar configuration patterns
- [MCP Tools Reference](../../../reference/mcp-tools.md) - Complete tool documentation

