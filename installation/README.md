# prAxIs OS Installation Guide

**How to install prAxIs OS into a target project**

---

## 🎯 Quick Start (For LLMs)

**⚠️ IMPORTANT: Use the automated script (recommended). Manual files are for reference/troubleshooting only.**

When a user asks to install prAxIs OS, follow this two-phase approach:

### Phase 1: Mechanical Installation (Automated Script) ⭐ RECOMMENDED

Run the installation script:

```bash
# macOS / Linux
curl -sSL https://raw.githubusercontent.com/honeyhiveai/praxis-os/main/scripts/install-praxis-os.py | python3 -

# Windows: Not yet supported
```

**What it does:**
- Clones repository to temp directory
- Creates `.praxis-os/` directory structure
- Copies standards, workflows, MCP server, scripts
- Creates Python venv and installs dependencies
- Configures .gitignore
- Cleans up temp files

**Time:** 2-3 minutes

### Phase 2: Agent Configuration (LLM-Guided)

After the script completes, configure the specific agent:

1. **Parse the agent from user's install command**:
   - `"...for Cursor"` → Primary Cursor setup
   - `"...for Cline in VS Code"` → Primary Cline
   - `"...for Cline in Cursor"` → Secondary Cline (HTTP)
   - `"...for Claude Code"` → **CLI/terminal mode** (default when no IDE specified)
   - `"...for Claude Code in VS Code"` → **VS Code extension** (when IDE specified)
   
   **Branching Logic for Claude Code:**
   - If user says `"for Claude Code"` → Route to `claude-code/terminal.md` (CLI mode)
   - If user says `"for Claude Code in VS Code"` → Route to `claude-code/vscode.md` (VS Code extension)
   - If user is IN VS Code but says `"for Claude Code"` → Consider asking if they want VS Code extension or CLI

2. **Read agent-specific guide**:
   - See `docs/content/how-to-guides/agent-integrations/`
   - Each agent has detailed setup instructions

3. **Follow the guide to**:
   - Configure MCP server settings
   - Set up agent-specific behavioral trigger files:
     - **Cursor**: `.cursorrules` (project root)
     - **Cline**: `.clinerules` (project root)
     - **Claude Code**: `.claude/CLAUDE.md` (or `CLAUDE.md` for CLI)
     - **GitHub Copilot**: `.github/copilot-instructions.md`
   - Copy helper scripts (for secondary agents only)
   - Verify installation

**Time:** 2-5 minutes

---

## 📖 Installation Methods

### Method 1: Automated Script (Recommended)

Run `install-praxis-os.py` for fast, reliable installation:

```bash
# From praxis-os repository
python scripts/install-praxis-os.py /path/to/target/project

# Or from target project  
python /path/to/praxis-os/scripts/install-praxis-os.py .
```

**What it does:**
- Clones repository to temp directory
- Creates `.praxis-os/` directory structure
- Copies all files (standards, workflows, MCP server)
- Creates Python venv and installs dependencies
- Configures .gitignore
- Schedules RAG index build
- Cleans up temp directory

**Time:** 2-3 minutes (mechanical operations only)

### Method 2: Manual Sequential Files (Reference/Troubleshooting)

**Note**: These files are primarily for **understanding the installation process** and **troubleshooting**. Use the automated script unless you have a specific reason to install manually.

For environments where script can't run, or for understanding/troubleshooting, use these sequential guides:

```
00-START.md → 01-directories.md → 02-copy-files.md → 
03-agent-configuration.md → 04-config-customization.md → 05-gitignore.md → 
06-venv-mcp.md → 07-validate.md → COMPLETE
```

**Each file:** ~200-250 lines, designed for vanilla LLM attention spans

**Time:** 5-10 minutes (manual steps + validation)

---

## 🎯 Design Principles

### Phase 1: Mechanical Installation

**The automated script handles "mechanical" operations:**
- File system operations (copy, create directories)
- Python venv creation
- Dependency installation
- Validation of file counts and structure

**Why script-based:**
- Fast (2-3 minutes vs 5-10 manual)
- Reliable (exact file counts, validated copies)
- No LLM attention span issues
- Repeatable and testable

### Phase 2: Agent Configuration

**Documentation handles "intelligent" decisions:**
- Which agent/IDE combination to use
- How to configure MCP for specific environment
- Primary vs secondary agent setup
- Troubleshooting agent-specific issues

**Why doc-based:**
- Each agent/IDE has unique configuration
- LLM can read and adapt instructions
- Troubleshooting requires understanding
- Reference material for users

---

## ⚠️ Critical Success Factors

### 1. Don't Litter Git Repos!

The source repo (`praxis-os`) is **cloned to a temp directory** and **deleted at the end**. We do NOT leave a git repo inside the consumer's project.

### 2. Don't Overwrite .cursorrules!

Many projects have existing `.cursorrules` files. Step 03 checks for this and offers merge options instead of blindly overwriting.

### 3. Create ALL Directories

The most common mistake: forgetting `.praxis-os/workflows/` directory. The MCP server's `ConfigValidator` requires it.

### 4. Use Correct Module Name

In `mcp.json`, use `"ouroboros"` NOT `"mcp_server"` or `"mcp_server.praxis_os_rag"`. The entry point is `ouroboros/__main__.py`.

---

## 📚 Documentation Structure

### Installation Process

1. **install-praxis-os.py** - ⭐ **Automated mechanical installation (RECOMMENDED)**
2. **00-START.md through 06-validate.md** - Manual sequential guides (reference/troubleshooting only)
3. **This README** - Overview and decision guidance

### Agent Integration (After Mechanical Installation)

Located in `docs/content/how-to-guides/agent-integrations/`:

**Primary Agents (Control MCP Server):**
- `cursor/` - Cursor IDE with native MCP support
- `cline/vscode.md` - Cline extension in VS Code
- `claude-code/terminal.md` - Claude Code CLI
- `claude-code/vscode.md` - Claude Code in VS Code

**Secondary Agents (Connect via HTTP):**
- `cline/cursor.md` - Cline connecting to Cursor's MCP server
- `claude-code/cursor.md` - Claude Code connecting to Cursor's MCP server

**Overview:**
- `README.md` - Decision tree, primary vs secondary, LLM support

---

## 🏗️ Architecture Context

**Source Repository** (this repo):
```
praxis-os/
├── installation/          ← Installation guides
│   ├── 00-START.md       ← Entry point
│   ├── 01-directories.md
│   ├── 02-copy-files.md
│   ├── 03-agent-configuration.md  ← Routes to agent-specific guides
│   ├── 04-config-customization.md  ← Customize mcp.yaml for project
│   ├── 05-gitignore.md
│   ├── 06-venv-mcp.md
│   └── 07-validate.md
├── universal/             ← Content to copy
│   ├── standards/
│   ├── usage/
│   └── workflows/
├── dist/ouroboros/        ← Server code to copy
└── .cursorrules           ← Cursor behavioral triggers (agent-specific files handled in step 03)
```

**During Installation** (temp directory):
```
/tmp/praxis-os-install-xyz/
└── [same structure as above]
    ← Cloned here temporarily
    ← Deleted at end of step 05
```

**Target Project** (consumer):
```
target-project/
├── .praxis-os/             ← Created during installation
│   ├── standards/
│   ├── usage/
│   ├── workflows/
│   ├── ouroboros/
│   ├── venv/
│   └── .cache/
├── [agent-specific file]  ← Copied or merged based on agent:
│                           - Cursor: .cursorrules
│                           - Cline: .clinerules
│                           - Claude Code: .claude/CLAUDE.md or CLAUDE.md
│                           - GitHub Copilot: .github/copilot-instructions.md
└── [agent config dir]/    ← Agent-specific config directory:
    └── mcp.json            - Cursor: .cursor/mcp.json
                              - Cline: .vscode/settings.json
                              - Claude Code: .vscode/settings.json or ~/.config/claude-code/mcp.json
                              - GitHub Copilot: .vscode/mcp.json or IDE-specific
```

---

## ✅ Validation

After installation, these should all be true:

```python
checks = {
    ".praxis-os/workflows/": exists and has ~47 files,
    ".praxis-os/venv/": exists with working Python,
    ".praxis-os/.cache/indexes/": exists with RAG index,
    ".cursorrules": exists with prAxIs OS rules,
    ".cursor/mcp.json": exists with "ouroboros" module,
    "Temp directory": deleted (cleaned up),
}
```

---

## 🚨 Common Failure Modes

| Issue | Cause | Fix |
|-------|-------|-----|
| Missing workflows/ | Forgot step 01 | Create `.praxis-os/workflows/` |
| Wrong module name | Used `mcp_server` or `mcp_server.praxis_os_rag` | Change to `ouroboros` in mcp.json |
| Empty workflows/ | Forgot step 02 | Copy files from `universal/workflows/` |
| Git repo left behind | Forgot step 05 | Delete temp directory manually |
| Agent file overwritten | Didn't follow step 03 | Restore from backup (`.cursorrules.backup`, `.clinerules.backup`, etc.) |
| Wrong agent file | Used wrong file for agent | Check agent detection in step 03, use correct file |

---

## 📖 For Maintainers

### When Updating Installation Process

1. Update the sequential files (00-06)
2. Keep each file ~200-250 lines
3. Maintain chain navigation
4. Update this README
5. Test on fresh project

### Critical Safety Rules

1. ⚠️ Never leave temp directory behind
2. ⚠️ Never blindly overwrite .cursorrules
3. ⚠️ Always validate at each step
4. ⚠️ Always backup user files before modifying

---

## 🎯 Success Criteria

Installation is successful when:
- ✅ All 8 directories created
- ✅ ~106 files copied
- ✅ .cursorrules handled safely
- ✅ Python venv working
- ✅ **RAG index built** (enables semantic search)
- ✅ mcp.json configured correctly
- ✅ **Temp directory deleted**
- ✅ MCP server validation passes

**Installation time**: ~5-10 minutes  
**Success rate**: Expected 100% (with proper guides)

---

**Last Updated**: October 8, 2025  
**Version**: 2.0 (Horizontally-scaled, bootstrapping-friendly)
