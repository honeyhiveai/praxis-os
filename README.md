# Agent OS Enhanced - Portable Multi-Agent Development Framework

**A portable Agent OS implementation with MCP RAG, sub-agents, and universal CS fundamentals.**

## 🎯 Overview

Agent OS Enhanced is a portable development framework that combines:
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

The Cursor agent will:
1. Analyze your project (detect language, frameworks)
2. Copy universal standards (static CS fundamentals)
3. Generate language-specific standards (tailored to your project)
4. Install MCP server locally (.agent-os/mcp_server/)
5. Configure Cursor (.cursor/mcp.json)
6. Build RAG index
```

### What Gets Installed

```
your-project/
├── .cursorrules              # Universal (27 lines, copied from repo)
├── .agent-os/
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
├── .cursorrules                  # Universal behavioral triggers (27 lines)
├── installation-guide.md         # Instructions for Cursor agent
│
├── universal/                    # Static CS fundamentals (rarely changes)
│   └── standards/
│       ├── concurrency/          # Race conditions, deadlocks, locking
│       ├── failure-modes/        # Graceful degradation, retries, circuit breakers
│       ├── architecture/         # Dependency injection, API design, separation of concerns
│       ├── testing/              # Test pyramid, test doubles, property-based testing
│       └── documentation/        # Code comments, API docs, README templates
│
├── language-instructions/        # Instructions for LLM to generate language-specific content
│   ├── python.md                 # How to generate Python-specific standards
│   ├── go.md                     # How to generate Go-specific standards
│   ├── javascript.md             # How to generate JavaScript-specific standards
│   ├── typescript.md             # How to generate TypeScript-specific standards
│   ├── rust.md                   # How to generate Rust-specific standards
│   ├── java.md                   # How to generate Java-specific standards
│   └── csharp.md                 # How to generate C#-specific standards
│
└── mcp_server/                   # MCP server implementation (gets updates)
    ├── __main__.py               # Main MCP server entry point
    ├── rag_engine.py             # LanceDB vector search
    ├── workflow_engine.py        # Phase-gated workflows
    ├── framework_generator.py    # Dynamic workflow creation
    ├── config/                   # Configuration management
    ├── models/                   # Data models
    ├── server/                   # Server factory & tools
    ├── requirements.txt          # MCP server dependencies
    └── CHANGELOG.md              # Version history
```

## 🎯 Design Philosophy

### What's Universal (Static, Rarely Changes)

- **`.cursorrules`**: Behavioral triggers and MCP routing (27 lines, language-agnostic)
- **`universal/standards/`**: CS fundamentals (race conditions, test pyramid, API design)
- **`language-instructions/`**: Instructions for LLM to generate content (stable)

### What's Generated (Per Project, Context-Aware)

- **`.agent-os/standards/development/`**: Language-specific standards (Python: GIL, Go: goroutines, etc.)
- **Project context integration**: References your actual frameworks, tools, and patterns

### What Gets Updated (Version Releases)

- **`mcp_server/`**: New features, bug fixes, performance improvements

---

## 🔧 Development & Dogfooding

**This repository dogfoods Agent OS - we use our own framework to develop itself.**

### True Dogfooding (No Shortcuts)

Our `.agent-os/` directory is a **real installation** with copied files (not symlinks):

```
agent-os-enhanced/
├── universal/                    # ← Framework SOURCE (edit this)
│   ├── standards/
│   ├── usage/
│   └── workflows/
│
├── .agent-os/                    # ← LOCAL INSTALL (like consumers)
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

# 2. Copy to .agent-os/ (like consumers do)
cp -r universal/standards .agent-os/standards/universal

# 3. File watcher auto-rebuilds RAG index
# (no manual rebuild needed!)

# 4. Test in Cursor
# Query MCP to verify changes

# 5. Commit both
git add universal/ .agent-os/standards/universal/
git commit -m "docs: update checklist"
```

**Why this workflow?**
- Tests installation every time we edit
- Catches bugs consumers would hit
- No special shortcuts = real dogfooding

See `.agent-os/standards/development/agent-os-architecture.md` for detailed explanation and `CONTRIBUTING.md` for contribution guidelines.

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
