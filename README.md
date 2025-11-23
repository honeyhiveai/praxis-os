# prAxIs OS
### *praxis, the ai os*

**A portable prAxIs OS implementation with MCP RAG, sub-agents, and universal CS fundamentals.**

## 🎯 Overview

prAxIs OS is a portable development framework that combines:
- **Universal CS Fundamentals**: Timeless patterns applicable to any language
- **Language-Specific Generation**: LLM generates tailored guidance per project
- **MCP RAG Server**: Semantic search over standards with 90% context reduction
- **Specialized Sub-Agents**: Design validation, concurrency analysis, test generation
- **Conversational Installation**: Cursor agent installs and configures everything

## 📖 Documentation

**Full documentation available at:** https://honeyhiveai.github.io/praxis-os/

The documentation site includes:
- Comprehensive guides and tutorials
- Architecture deep-dives
- Case studies on AI-authored development
- API references and workflow documentation

## 🚀 Installation

### For Users

**Open your project in Cursor, Claude Code, Cline, or GitHub Copilot and say:**

```
"Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> [in <IDE>]"
```

**Examples:**
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Cursor"`
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Cline in VS Code"`
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Cline in Cursor"` (secondary)
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Claude Code"` (CLI)
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for Claude Code in VS Code"` (VS Code extension)
- `"Install prAxIs OS from github.com/honeyhiveai/praxis-os for GitHub Copilot"`

Your AI agent will handle the complete installation automatically.

**Time:** ~5-10 minutes

---

### For LLMs (You Are Here!)

When a user asks to install prAxIs OS, follow this two-phase approach:

**⚠️ IMPORTANT: Use the automated script (recommended). Manual files are for reference/troubleshooting only.**

#### Phase 1: Mechanical Installation (Automated Script) ⭐ RECOMMENDED

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

#### Phase 2: Agent Configuration (LLM-Guided)

After the script completes, **parse the user's command** and route to the correct agent-specific guide:

**⚠️ CRITICAL: The LLM calling this installation knows what agent/IDE it's running in. Parse the agent/IDE from the user's installation command.**

**Command Pattern:**
```
Install prAxIs OS from github.com/honeyhiveai/praxis-os for <AGENT> (optional: in <IDE>)
```

**Required**: `for <AGENT>`  
**Optional**: `in <IDE>` (if not specified, IDE is implied based on agent)

1. **Parse User's Command**:
   
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
       detected = {"agent": "claude-code", "ide": "terminal", "mode": "primary"}
   elif "for GitHub Copilot" in user_command or "for Copilot" in user_command:
       detected = {"agent": "github-copilot", "ide": "vscode", "mode": "primary"}
   
   if not detected:
       print("⚠️  Agent/IDE not specified in command")
       print("Please specify: 'for Cursor', 'for Cline in VS Code', 'for Claude Code', etc.")
   ```

2. **Route to Correct Agent-Specific Guide**:
   
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
   guide_path = routing_table.get(key)
   
   if not guide_path:
       print(f"❌ Unknown agent/IDE combination: {detected}")
       print("Available options:")
       print("  - Cursor (primary)")
       print("  - Cline in VS Code (primary)")
       print("  - Cline in Cursor (secondary)")
       print("  - Claude Code (CLI/terminal)")
       print("  - Claude Code in VS Code")
       print("  - GitHub Copilot")
   ```

3. **Read Agent-Specific Guide**:
   - See [`docs/content/how-to-guides/agent-integrations/`](docs/content/how-to-guides/agent-integrations/)
   - Each agent has detailed setup instructions

4. **Follow the Guide to**:
   - Configure MCP server settings (agent-specific config files)
   - Set up agent-specific behavioral trigger files:
     - **Cursor**: `.cursorrules` (project root)
     - **Cline**: `.clinerules` (project root)
     - **Claude Code**: `.claude/CLAUDE.md` (or `CLAUDE.md` for CLI)
     - **GitHub Copilot**: `.github/copilot-instructions.md`
   - Copy helper scripts (for secondary agents only)
   - Verify installation

**Time:** 2-5 minutes

**📖 For complete command parsing logic and routing table**: See [`installation/03-agent-configuration.md`](installation/03-agent-configuration.md)

---

### Installation Documentation

**For LLMs installing prAxIs OS:**

- **Quick Start**: See [`installation/README.md`](installation/README.md) for the complete installation flow
- **Automated Script**: Recommended approach (handles mechanical operations)
- **Manual Guides**: See [`installation/00-START.md`](installation/00-START.md) through [`installation/07-validate.md`](installation/07-validate.md) for step-by-step manual installation (reference/troubleshooting only)

**For Users:**

- **Agent-Specific Setup**: After mechanical installation, see [`docs/content/how-to-guides/agent-integrations/`](docs/content/how-to-guides/agent-integrations/) for your specific agent/IDE combination
- **Troubleshooting**: See [`installation/README.md`](installation/README.md) for common issues and solutions

### What Gets Installed

```
your-project/
├── .cursorrules              # Universal (26 lines, copied from repo)
├── .praxis-os/
│   ├── standards/
│   │   ├── universal/        # Copied from this repo
│   │   └── development/      # Generated for your language
│   ├── mcp_server/           # Copied from this repo
│   └── .cache/vector_index/  # RAG index of YOUR standards
└── .cursor/
    └── mcp.json              # Points to local MCP server
```

## 📁 Repository Structure

```
praxis-os/
├── README.md                     # This file
├── .cursorrules                  # Universal behavioral triggers (26 lines)
│
├── installation/                 # Installation guides (start here for LLMs)
│   ├── 00-START.md              # Entry point - clone to temp, setup
│   ├── 01-directories.md        # Create all required directories
│   ├── 02-copy-files.md         # Copy files from source
│   ├── 03-agent-configuration.md  # Route to agent-specific guides
│   ├── 04-venv-mcp.md           # Python venv + mcp.json
│   ├── 05-validate.md           # Validate + cleanup temp files
│   └── README.md                # Installation system overview
│
├── universal/                    # Content copied to target projects
│   ├── standards/               # Universal CS fundamentals
│   │   ├── concurrency/         # Race conditions, deadlocks, locking
│   │   ├── failure-modes/       # Graceful degradation, retries, circuit breakers
│   │   ├── architecture/        # Dependency injection, API design, separation of concerns
│   │   ├── testing/             # Test pyramid, test doubles, property-based testing
│   │   └── documentation/       # Code comments, API docs, README templates
│   │   └── mcp-usage-guide.md   # MCP tool reference
│   └── workflows/               # Phase-gated workflow definitions
│       ├── spec_creation_v1/    # Spec creation workflow
│       └── spec_execution_v1/   # Spec execution workflow
│
└── mcp_server/                   # MCP server (copied to target projects)
   ├── __main__.py               # Main entry point
   ├── rag_engine.py             # LanceDB vector search
   ├── workflow_engine.py        # Phase-gated workflows
   ├── framework_generator.py    # Dynamic workflow creation
   ├── config/                   # Configuration management
   ├── models/                   # Data models
   ├── server/                   # Server factory & tools
   ├── requirements.txt          # MCP server dependencies
   └── CHANGELOG.md              # Version history
```

**For AI Installing prAxIs OS**: Start at [`installation/00-START.md`](installation/00-START.md)

## 🎯 Design Philosophy

### What's Universal (Copied to All Projects)

- **`.cursorrules`**: Behavioral triggers and MCP routing (26 lines, language-agnostic)
- **`dist/universal/standards/`**: CS fundamentals (race conditions, test pyramid, API design) - distributed
- **`dist/universal/workflows/`**: Phase-gated workflow definitions - distributed

### What's Generated (Optional, Context-Aware)

- **`.praxis-os/standards/development/`**: Language-specific standards (Python: GIL, Go: goroutines, etc.)
- **Project context integration**: References your actual frameworks, tools, and patterns

### What Gets Updated (Version Releases)

- **`mcp_server/`**: New features, bug fixes, performance improvements
- **`universal/`**: New standards, workflows, or usage docs

---

## 🔧 Development & Dogfooding

**This repository dogfoods prAxIs OS - we use our own framework to develop itself.**

### True Dogfooding (No Shortcuts)

Our `.praxis-os/` directory is a **real installation** with copied files (not symlinks):

```
praxis-os/
├── dist/
│   └── universal/              # ← DISTRIBUTION ARTIFACTS (synced to consumers)
│       ├── standards/
│       └── workflows/
│
├── .praxis-os/                  # ← LOCAL INSTALL (dogfooding, like consumers)
│   ├── standards/               # ✅ SYNCED from dist/universal/standards/
│   ├── workflows/               # ✅ SYNCED from dist/universal/workflows/
│   ├── standards/development/   # Project-specific (Python guidance)
│   ├── .cache/                  # RAG index
│   └── venv/                    # MCP server virtualenv
```

**Why No Symlinks?**
- ✅ Same installation process as consumers
- ✅ Catches copy/path bugs before shipping
- ✅ Validates update workflow
- ✅ Feels all consumer pain points

### Development Workflow

**Editing Framework Source:**
```bash
# 1. Edit source
vim universal/standards/ai-safety/production-code-checklist.md

# 2. Copy to .praxis-os/ (like consumers do)
cp -r universal/standards .praxis-os/standards/universal

# 3. File watcher auto-rebuilds RAG index
# (no manual rebuild needed!)

# 4. Test in Cursor
# Query MCP to verify changes

# 5. Commit both
git add universal/ .praxis-os/standards/universal/
git commit -m "docs: update checklist"
```

**Why this workflow?**
- Tests installation every time we edit
- Catches bugs consumers would hit
- No special shortcuts = real dogfooding

See `.praxis-os/standards/development/agent-os-architecture.md` for detailed explanation and `CONTRIBUTING.md` for contribution guidelines.

---

## 🔥 Key Benefits

1. **Portable**: Install once as git repo, works in any project
2. **Adaptive**: Same standards, different language contexts
3. **Intelligent**: RAG + sub-agents provide targeted guidance
4. **Conversational**: Cursor agent handles installation and configuration
5. **Isolated**: Each project owns its prAxIs OS installation
6. **Versionable**: Project controls which prAxIs OS version to use
7. **Customizable**: Generated standards can be tuned per project

## 🚀 Usage After Installation

Once installed in your project, use MCP tools:

```
# Search standards
"What are the concurrency best practices?"
→ Queries RAG, returns language-specific guidance

# Use workflows
"Start spec creation workflow for user authentication feature"
→ Structured workflow with phase gates and validation

# Generate new workflows
"Create a new workflow for API documentation"
→ Framework generator creates compliant workflow structure

# Query specific phase/task
"Show me Phase 0 Task 1 of the current workflow"
→ Returns detailed task instructions with commands
```

## 🌐 Dual-Transport Architecture (New!)

**Multi-Agent Collaboration with Zero Conflicts**

prAxIs OS now supports **dual-transport mode**, enabling seamless multi-agent workflows:

### Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Your Project                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Main IDE (Cursor/Windsurf)                        │
│        │                                            │
│        │ stdio                                      │
│        ▼                                            │
│  ┌──────────────────────┐                          │
│  │   MCP Server         │                          │
│  │   (Dual Transport)   │                          │
│  │                      │                          │
│  │  stdio ◄──► http     │                          │
│  └──────────────────────┘                          │
│        ▲                                            │
│        │ HTTP                                       │
│        │                                            │
│  Sub-Agents (Cline, Aider, Custom Scripts)         │
│        │                                            │
│        │ Auto-discovery via                         │
│        │ .praxis-os/.mcp_server_state.json           │
└─────────────────────────────────────────────────────┘
```

### Key Features

#### 🔌 Multi-Transport Support

- **Main IDE**: Connects via stdio (standard MCP)
- **Sub-agents**: Connect via HTTP (auto-discovered)
- **No configuration needed**: Sub-agents auto-discover the HTTP endpoint

#### 🚀 Zero-Conflict Multi-Project

Run multiple prAxIs OS projects simultaneously:
- Each project gets a unique port (auto-allocated from `4242-5242`)
- No manual port configuration required
- Works across multiple IDE instances

#### 🔍 Auto-Discovery

Sub-agents discover the MCP server automatically:

```python
from mcp_server.sub_agents import discover_mcp_server

# Find the server (reads .praxis-os/.mcp_server_state.json)
url = discover_mcp_server()
if url:
    # Connect and use tools
    ...
```

#### 📊 State File

Server writes connection info to `.praxis-os/.mcp_server_state.json`:

```json
{
  "transport": "dual",
  "url": "http://127.0.0.1:4242/mcp",
  "port": 4242,
  "pid": 12345,
  "project": {"name": "my-project"},
  "started_at": "2025-10-11T14:30:00Z"
}
```

### Usage

#### Enable Dual Transport

**File:** `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual"
      ],
      "transport": "stdio"
    }
  }
}
```

#### Sub-Agent Integration

**Example: Cline**  
Cline auto-discovers the server, no config needed!

**Example: Python SDK**

```python
from mcp_server.sub_agents import connect_and_use_mcp_server
import asyncio

result = asyncio.run(connect_and_use_mcp_server())
print(result)  # {'success': True, 'tools': [...], ...}
```

**Example: Aider**

```python
from mcp_server.sub_agents import discover_mcp_server

url = discover_mcp_server()
# Use url with your HTTP client
```

### Configuration Examples

See `.praxis-os/specs/2025-10-11-mcp-dual-transport/IDE-CONFIGURATION.md` for:
- Cursor setup
- Windsurf setup
- Claude Desktop setup
- Sub-agent integration examples
- Troubleshooting guide

### Backwards Compatibility

**No breaking changes!** Existing configs work as-is:
- Omitting `--transport dual` defaults to stdio-only mode
- All existing IDE configurations continue to work
- Upgrade when you need multi-agent support

### Benefits

| Feature | Stdio-Only | **Dual Transport** |
|---------|-----------|-------------------|
| IDE connection | ✅ | ✅ |
| Sub-agent support | ❌ | **✅** |
| Multi-project | Manual | **✅ Zero-config** |
| Auto-discovery | N/A | **✅** |
| Thread-safe | ✅ | **✅** |
| State monitoring | ❌ | **✅** |

**Recommendation:** Use dual transport for all new projects

## 📊 Maintenance Model

### Updating prAxIs OS in Your Project

```
"Update prAxIs OS to latest version"

Cursor agent will:
1. Pull latest from this repo
2. Update MCP server code
3. Update universal standards (if changed)
4. Preserve your customizations
5. Rebuild RAG index
```

### Contributing Back

Found a great pattern in your project? Contribute it back:

1. Test it in your project for months
2. PR to this repo's `universal/standards/` or `language-instructions/`
3. Community benefits from your learning

## 🎯 Credits

- **Foundation**: [Builder Methods prAxIs OS](https://buildermethods.com/agent-os) by Brian Casel
- **Evolution**: HoneyHive's LLM Workflow Engineering methodology
- **Implementation**: MCP/RAG architecture with specialized sub-agents

## 📝 License

MIT License - Use freely in any project

---

**Start building with AI agents, enhanced.**
