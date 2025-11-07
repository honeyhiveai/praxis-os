# Step 3: Configure Agent Integration

**Previous**: `02-copy-files.md` (copied content files)  
**Current**: Route to agent-specific configuration guide  
**Next**: `04-gitignore.md` (after agent config complete)

---

## 🎯 What This Step Does

After mechanical installation completes, you need to configure your specific AI agent. This step routes you to the correct agent-specific guide based on the user's installation command.

**Why this step exists**: Each agent (Cursor, Cline, Claude Code, GitHub Copilot) has different configuration files and setup requirements. This branch handler ensures you follow the right guide.

**Time**: Routing takes seconds, actual configuration takes 2-5 minutes

---

## 🔀 Step 1: Parse User's Command

**⚠️ CRITICAL: The LLM calling this installation knows what agent/IDE it's running in. Parse the agent/IDE from the user's installation command.**

The user's installation command follows this pattern:
```
Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> (optional: in <IDE>)
```

**Required**: `for <AGENT>`  
**Optional**: `in <IDE>` (if not specified, IDE is implied based on agent)

Parse it to route to the correct guide:

```python
# Extract agent from user's command
# Pattern: "Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> (optional: in <IDE>)"

user_command = "Install prAxIs OS from github.com/honeyhiveai/praxis-os for Claude Code in VS Code"
# Examples:
#   "for Cursor" → Cursor (IDE implied: Cursor)
#   "for Cline in VS Code" → Cline in VS Code
#   "for Cline in Cursor" → Cline in Cursor (secondary)
#   "for Claude Code" → Claude Code CLI (no IDE = terminal)
#   "for Claude Code in VS Code" → Claude Code in VS Code
#   "for GitHub Copilot" → GitHub Copilot (IDE implied: VS Code)

# Parse agent specification from user's command
detected = None

if "for Cursor" in user_command:
    detected = {"agent": "cursor", "ide": "cursor", "mode": "primary"}
    
elif "for Cline in VS Code" in user_command:
    detected = {"agent": "cline", "ide": "vscode", "mode": "primary"}
    
elif "for Cline in Cursor" in user_command:
    detected = {"agent": "cline", "ide": "cursor", "mode": "secondary"}
    
elif "for Claude Code in VS Code" in user_command:
    detected = {"agent": "claude-code", "ide": "vscode", "mode": "primary"}
    
elif "for Claude Code" in user_command:
    # Default to CLI when no IDE specified
    detected = {"agent": "claude-code", "ide": "terminal", "mode": "primary"}
    
elif "for GitHub Copilot" in user_command or "for Copilot" in user_command:
    detected = {"agent": "github-copilot", "ide": "vscode", "mode": "primary"}

if not detected:
    # User didn't specify agent - show all options
    print("⚠️  Agent/IDE not specified in command")
    print("Please specify in your command:")
    print("  - 'for Cursor'")
    print("  - 'for Cline in VS Code'")
    print("  - 'for Cline in Cursor'")
    print("  - 'for Claude Code' (CLI)")
    print("  - 'for Claude Code in VS Code'")
    print("  - 'for GitHub Copilot' or 'for Copilot'")
    exit(1)

print(f"✅ Parsed from command: Agent={detected['agent']}, IDE={detected['ide']}, Mode={detected['mode']}")
```

## 🗺️ Step 2: Route to Correct Guide

```python
routing_table = {
    ("cursor", "cursor", "primary"): "docs/content/how-to-guides/agent-integrations/cursor/index.md",
    ("cline", "vscode", "primary"): "docs/content/how-to-guides/agent-integrations/cline/vscode.md",
    ("cline", "cursor", "secondary"): "docs/content/how-to-guides/agent-integrations/cline/cursor.md",
    ("claude-code", "vscode", "primary"): "docs/content/how-to-guides/agent-integrations/claude-code/vscode.md",
    ("claude-code", "terminal", "primary"): "docs/content/how-to-guides/agent-integrations/claude-code/terminal.md",
    ("claude-code", "cursor", "secondary"): "docs/content/how-to-guides/agent-integrations/claude-code/cursor.md",
    ("github-copilot", "vscode", "primary"): "docs/content/how-to-guides/agent-integrations/github-copilot/index.md",
}

key = (detected["agent"], detected["ide"], detected["mode"])
guide = routing_table.get(key)

if not guide:
    print(f"❌ Unknown agent/IDE combination: {detected}")
    print("Available options:")
    print("  - Cursor (primary)")
    print("  - Cline in VS Code (primary)")
    print("  - Cline in Cursor (secondary)")
    print("  - Claude Code (CLI/terminal)")
    print("  - Claude Code in VS Code")
    print("  - GitHub Copilot")
    exit(1)

print(f"✅ Routing to: {guide}")
print(f"   Agent: {detected['agent']}, IDE: {detected['ide']}, Mode: {detected['mode']}")
```

---

## 📋 Routing Table

| User Command | Agent | Guide Path |
|--------------|-------|------------|
| `"for Cursor"` | Cursor IDE | `docs/content/how-to-guides/agent-integrations/cursor/index.md` |
| `"for Cline in VS Code"` | Cline (VS Code) | `docs/content/how-to-guides/agent-integrations/cline/vscode.md` |
| `"for Cline in Cursor"` | Cline (Secondary) | `docs/content/how-to-guides/agent-integrations/cline/cursor.md` |
| `"for Claude Code"` | Claude Code CLI | `docs/content/how-to-guides/agent-integrations/claude-code/terminal.md` |
| `"for Claude Code in VS Code"` | Claude Code VS Code | `docs/content/how-to-guides/agent-integrations/claude-code/vscode.md` |
| `"for GitHub Copilot"` or `"for Copilot"` | GitHub Copilot | `docs/content/how-to-guides/agent-integrations/github-copilot/index.md` |

**Branching Logic for Claude Code:**
- `"for Claude Code"` (no IDE specified) → **CLI/terminal mode** → `claude-code/terminal.md`
- `"for Claude Code in VS Code"` (IDE specified) → **VS Code extension** → `claude-code/vscode.md`

---

## 🎯 Next Action: Read Agent-Specific Guide

After routing, read the agent-specific guide:

```python
guide_path = f"{PRAXIS_OS_SOURCE}/{guide}"

print(f"\n📖 Reading agent configuration guide: {guide_path}")
print("   This guide will walk you through:")
print("   - Configuring agent-specific files (.cursorrules, mcp.json, etc.)")
print("   - Handling existing configuration files safely")
print("   - Verifying the installation")
print("   - Troubleshooting agent-specific issues")
```

**Each agent guide handles:**
- ✅ Agent-specific configuration files (`.cursorrules`, `.cursor/mcp.json`, VS Code settings, etc.)
- ✅ Safe handling of existing files (merge, backup, replace options)
- ✅ File placement rules (where config files go)
- ✅ Verification steps
- ✅ Troubleshooting

---

## ⚠️ Important Notes

### File Handling Rules

Each agent guide contains detailed instructions for:
- **Checking for existing files** before overwriting
- **Merging strategies** (auto-merge, manual merge, backup-and-replace)
- **File placement** (project root, `.cursor/`, `.vscode/`, etc.)
- **Backup creation** before modifications

**Never blindly overwrite user configuration files!**

### Agent-Specific Config Files

Different agents use different configuration files:

| Agent | Config Files |
|-------|--------------|
| **Cursor** | `.cursorrules`, `.cursor/mcp.json` |
| **Cline** | `.clinerules`, `.vscode/settings.json` (or Cline UI) |
| **Claude Code (VS Code)** | `.claude/CLAUDE.md`, `.vscode/settings.json` |
| **Claude Code (CLI)** | `.claude/CLAUDE.md`, `~/.config/claude-code/mcp.json` or project `.mcp.json` |
| **GitHub Copilot** | `.github/copilot-instructions.md`, `.vscode/mcp.json` (VS Code) or IDE-specific `mcp.json` |

Each guide explains where these files go and how to handle existing ones.

---

## ✅ Validation Checkpoint #3

After routing to agent guide, verify:

```python
import os

# Check that agent guide exists
if not os.path.exists(guide_path):
    print(f"❌ Agent guide not found: {guide_path}")
    print("   Check that PRAXIS_OS_SOURCE is correct")
    exit(1)

print(f"✅ Agent guide found: {guide_path}")
print("   Ready to proceed with agent configuration")
```

---

## 📊 Progress Check

At this point you should have:
- ✅ Mechanical installation complete (from script or steps 01-02)
- ✅ Agent identified from user's command
- ✅ Correct guide path determined
- ✅ Ready to read agent-specific configuration guide

**If anything above is ❌, stop and fix before continuing.**

---

## 🎯 What's Next

You've routed to the correct agent guide. Now:

1. **Read the agent-specific guide** (path determined above)
2. **Follow the guide** to configure:
   - Agent-specific config files
   - MCP server settings
   - File handling (merge existing files safely)
3. **Verify installation** per agent guide
4. **Continue to step 04** (config customization)

---

## ➡️ NEXT STEP

**Read file**: The agent-specific guide determined above

**Then**: `installation/04-config-customization.md`

That file will:
1. Guide you through customizing `mcp.yaml` config file
2. Update code indexing paths to match your project structure
3. Configure languages for your project
4. Direct you to step 05 (gitignore configuration)

---

**Status**: Step 3 Complete ✅  
**Routed**: To agent-specific configuration guide  
**Next File**: Agent guide (determined above) → then `04-config-customization.md`  
**Step**: 3 of 7

