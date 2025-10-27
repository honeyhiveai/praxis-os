# prAxIs OS
### *praxis, the ai os*

**A portable Agent OS implementation with MCP RAG, sub-agents, and universal CS fundamentals.**

## 🎯 Overview

prAxIs OS is a portable development framework that combines:
- **Universal CS Fundamentals**: Timeless patterns applicable to any language
- **Language-Specific Generation**: LLM generates tailored guidance per project
- **MCP RAG Server**: Semantic search over standards with 90% context reduction
- **Specialized Sub-Agents**: Design validation, concurrency analysis, test generation
- **Conversational Installation**: Cursor agent installs and configures everything

## 📖 Documentation

**Full documentation available at:** https://honeyhiveai.github.io/agent-os-enhanced/

The documentation site includes:
- Comprehensive guides and tutorials
- Architecture deep-dives
- Case studies on AI-authored development
- API references and workflow documentation

## 🚀 Installation

### For Users (In Your Project)

```
Open your project in Cursor and say:
"Install Agent OS from github.com/honeyhiveai/agent-os-enhanced"
```

The Cursor agent will follow the installation guide in `installation/` directory:
1. Clone source to temp directory
2. Create all required directories
3. Copy universal standards, workflows, and MCP server
4. Handle .cursorrules safely (won't overwrite existing!)
5. Create Python venv and configure Cursor
6. Clean up temp files

**For LLMs**: Start at [`installation/00-START.md`](installation/00-START.md)

**Total time**: ~5-10 minutes

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
agent-os-enhanced/
├── README.md                     # This file
├── .cursorrules                  # Universal behavioral triggers (26 lines)
│
├── installation/                 # Installation guides (start here for LLMs)
│   ├── 00-START.md              # Entry point - clone to temp, setup
│   ├── 01-directories.md        # Create all required directories
│   ├── 02-copy-files.md         # Copy files from source
│   ├── 03-cursorrules.md        # Safe .cursorrules handling
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
│   ├── usage/                   # Agent OS usage documentation
│   │   ├── creating-specs.md    # How to create specifications
│   │   ├── operating-model.md   # AI-human collaboration model
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

**For AI Installing Agent OS**: Start at [`installation/00-START.md`](installation/00-START.md)

## 🎯 Design Philosophy

### What's Universal (Copied to All Projects)

- **`.cursorrules`**: Behavioral triggers and MCP routing (26 lines, language-agnostic)
- **`universal/standards/`**: CS fundamentals (race conditions, test pyramid, API design)
- **`universal/workflows/`**: Phase-gated workflow definitions
- **`universal/usage/`**: Agent OS usage documentation

### What's Generated (Optional, Context-Aware)

- **`.praxis-os/standards/development/`**: Language-specific standards (Python: GIL, Go: goroutines, etc.)
- **Project context integration**: References your actual frameworks, tools, and patterns

### What Gets Updated (Version Releases)

- **`mcp_server/`**: New features, bug fixes, performance improvements
- **`universal/`**: New standards, workflows, or usage docs

---

## 🔧 Development & Dogfooding

**This repository dogfoods Agent OS - we use our own framework to develop itself.**

### True Dogfooding (No Shortcuts)

Our `.praxis-os/` directory is a **real installation** with copied files (not symlinks):

```
agent-os-enhanced/
├── universal/                    # ← Framework SOURCE (edit this)
│   ├── standards/
│   ├── usage/
│   └── workflows/
│
├── .praxis-os/                    # ← LOCAL INSTALL (like consumers)
│   ├── standards/universal/     # ✅ COPIED from ../universal/standards/
│   ├── usage/                   # ✅ COPIED from ../universal/usage/
│   ├── workflows/               # ✅ COPIED from ../universal/workflows/
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
5. **Isolated**: Each project owns its Agent OS installation
6. **Versionable**: Project controls which Agent OS version to use
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

Agent OS now supports **dual-transport mode**, enabling seamless multi-agent workflows:

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

Run multiple Agent OS projects simultaneously:
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
    "agent-os-rag": {
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

### Updating Agent OS in Your Project

```
"Update Agent OS to latest version"

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

- **Foundation**: [Builder Methods Agent OS](https://buildermethods.com/agent-os) by Brian Casel
- **Evolution**: HoneyHive's LLM Workflow Engineering methodology
- **Implementation**: MCP/RAG architecture with specialized sub-agents

## 📝 License

MIT License - Use freely in any project

---

**Start building with AI agents, enhanced.**
