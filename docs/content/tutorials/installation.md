---
sidebar_position: 2
doc_type: tutorial
---

# Installation

Install prAxIs OS in any project with a simple conversation. The Cursor agent handles everything automatically.

## Quick Start

```bash
# Open your project in Cursor and say:
"Install prAxIs OS from github.com/honeyhiveai/praxis-os"
```

The Cursor agent will:
1. **Analyze your project** - Detect language, frameworks, tools
2. **Copy universal standards** - Timeless CS fundamentals
3. **Generate language-specific standards** - Tailored to your stack
4. **Install MCP server** - Local Python process
5. **Configure Cursor** - MCP integration
6. **Build RAG index** - Semantic search ready

**Time:** ~5 minutes for complete installation

## What Gets Installed

```
your-project/
├── .cursorrules                  # 26 lines - AI behavioral triggers
├── .praxis-os/
│   ├── standards/
│   │   ├── universal/            # Copied from repo
│   │   │   ├── concurrency/      # Race conditions, deadlocks, etc.
│   │   │   ├── architecture/     # SOLID, DI, API design
│   │   │   ├── testing/          # Test pyramid, test doubles
│   │   │   ├── failure-modes/    # Circuit breakers, retries
│   │   │   └── security/         # Security patterns
│   │   └── development/          # Generated for your language
│   │       ├── python-concurrency.md  # (if Python project)
│   │       ├── python-testing.md
│   │       └── python-architecture.md
│   ├── usage/                    # How to use prAxIs OS
│   ├── workflows/                # Phase-gated workflows
│   │   ├── spec_creation_v1/
│   │   └── spec_execution_v1/
│   ├── mcp_server/               # MCP/RAG server (copied)
│   │   ├── __main__.py
│   │   ├── rag_engine.py
│   │   ├── workflow_engine.py
│   │   └── requirements.txt
│   ├── .cache/                   # Not tracked in git
│   │   └── vector_index/         # RAG index (auto-built)
│   └── venv/                     # MCP server virtualenv
└── .cursor/
    └── mcp.json                  # MCP server configuration
```

## Installation Steps (Detailed)

### 1. Project Analysis

Cursor agent analyzes your project:

```python
# Detects:
- Programming language (go.mod, package.json, pyproject.toml)
- Frameworks (Django, FastAPI, React, Next.js)
- Tools (pytest, jest, mypy, eslint)
- Patterns (async/await, REST, GraphQL)
```

### 2. Copy Universal Standards

```bash
# From repo → your project
cp -r praxis-os/universal/standards/ .praxis-os/standards/universal/
cp -r praxis-os/universal/usage/ .praxis-os/usage/
cp -r praxis-os/universal/workflows/ .praxis-os/workflows/
```

**What's copied:**
- Concurrency patterns (race conditions, deadlocks, locking)
- Architecture patterns (SOLID, DI, separation of concerns)
- Testing strategies (test pyramid, test doubles)
- Failure modes (circuit breakers, retry strategies)
- Security patterns
- Database patterns

### 3. Generate Language-Specific Standards

Cursor agent generates standards for your specific language:

**Python project example:**
```bash
# Cursor agent generates:
.praxis-os/standards/development/
├── python-concurrency.md        # GIL, threading, asyncio
├── python-testing.md            # pytest, unittest, coverage
├── python-architecture.md       # FastAPI/Django patterns
├── python-error-handling.md     # try/except, logging
└── python-code-quality.md       # mypy, black, ruff
```

**Content:**
- References universal standards
- Adds Python-specific implementations
- Includes your actual frameworks (FastAPI, Django, etc.)
- Your actual tools (pytest, mypy, black)
- Project-specific patterns found in your code

### 4. Install MCP Server

```bash
# Copy MCP server code
cp -r praxis-os/mcp_server/ .praxis-os/mcp_server/

# Create virtualenv
cd .praxis-os
python -m venv venv

# Install dependencies
./venv/bin/pip install -r mcp_server/requirements.txt
```

**Dependencies installed:**
```
lancedb~=0.25.0              # Vector database
sentence-transformers>=2.0.0  # Local embeddings
mcp>=1.0.0                    # Model Context Protocol
watchdog>=3.0.0               # File watching
```

### 5. Configure Cursor

Create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "mcp_server",
        "--transport",
        "dual",
        "--log-level",
        "INFO"
      ],
      "env": {
        "PROJECT_ROOT": "${workspaceFolder}",
        "PYTHONPATH": "${workspaceFolder}/.praxis-os",
        "PYTHONUNBUFFERED": "1"
      },
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state",
        "get_server_info"
      ]
    }
  }
}
```

**Transport Modes:**
- `dual`: stdio (IDE) + HTTP (sub-agents) - **Recommended**
- `stdio`: IDE communication only (traditional mode)
- `http`: Network communication only (for testing or services)

**Restart Cursor** to activate MCP server.

**Dual-Transport Benefits:**
- ✅ IDE integration via stdio
- ✅ Sub-agent access via HTTP (http://127.0.0.1:4242/mcp)
- ✅ Zero port conflicts (automatic port allocation)
- ✅ Multi-project support (each project gets its own port)

### 6. Build RAG Index

First time the MCP server starts, it builds the vector index:

```python
# Auto-runs on first startup
Building RAG index...
- Scanning .praxis-os/standards/
- Scanning .praxis-os/workflows/
- Chunking markdown files
- Generating embeddings
- Building vector index

Index built in 58s
- 450 chunks indexed
- Ready for queries
```

**After first build:**
- File watcher monitors changes
- Auto-rebuilds index when files change
- No manual rebuilds needed

## Verify Installation

### Check MCP Server

```bash
# In Cursor, say:
"Query MCP: What are race conditions?"
```

Should return relevant chunks from universal/development standards.

### Check Dual-Transport (if using dual mode)

```bash
# Check state file
cat .praxis-os/.mcp_server_state.json

# Should show:
# - transport: "dual"
# - port: 4242 (or another available port)
# - url: "http://127.0.0.1:4242/mcp"
# - project info

# Test HTTP endpoint
# In Cursor, say:
"Call get_server_info tool"

# Should show server info including transport mode
```

### Check Workflows

```bash
# In Cursor, say:
"Start spec creation workflow for user authentication"
```

Should initialize workflow and show Phase 0.

### Check Standards

```bash
# Check files were copied
ls -la .praxis-os/standards/universal/concurrency/
# Should see: race-conditions.md, deadlocks.md, etc.

ls -la .praxis-os/standards/development/
# Should see language-specific files
```

## Updating prAxIs OS

When new versions are released, use the upgrade workflow:

```bash
# In Cursor, say:
"Run the prAxIs OS upgrade workflow"
```

The `agent_os_upgrade_v1` workflow will:
1. ✅ Create automatic backup
2. ✅ Update standards, workflows, and MCP server
3. ✅ **Preserve your customizations** (specs, development standards)
4. ✅ Update `.gitignore` from standards
5. ✅ Validate everything works
6. ✅ Auto-rollback if anything fails

**Time:** ~3-4 minutes | **Safety:** Automatic backup and rollback

For detailed upgrade documentation, see **[Upgrading prAxIs OS](../how-to-guides/upgrading.md)**

## Manual Installation (Advanced)

If you prefer manual control:

```bash
# 1. Clone repo
git clone https://github.com/honeyhiveai/praxis-os.git

# 2. Copy to your project
cd your-project
cp praxis-os/.cursorrules .
cp -r praxis-os/universal .praxis-os/standards/universal
cp -r praxis-os/mcp_server .praxis-os/mcp_server

# 3. Setup MCP server
cd .praxis-os
python -m venv venv
./venv/bin/pip install -r mcp_server/requirements.txt

# 4. Configure Cursor
# Create .cursor/mcp.json (see above)

# 5. Generate language-specific standards
# Use Cursor agent or manual creation
```

## Troubleshooting

### MCP Server Not Starting

```bash
# Check logs
cat ~/.cursor/logs/mcp.log

# Common issues:
- Python version < 3.9
- Missing dependencies
- Invalid mcp.json config
```

### RAG Index Not Building

```bash
# Manual rebuild
cd .praxis-os
./venv/bin/python -c "
from mcp_server.rag_engine import RAGEngine
engine = RAGEngine(project_root='.')
engine.build_index()
"
```

### No Language-Specific Standards

Cursor agent may not have generated them. Manually create:

```bash
# Python example
cp praxis-os/language-instructions/python.md .praxis-os/
# Follow instructions to generate standards
```

## Requirements

- **Cursor**: Latest version
- **Python**: 3.9+ (for MCP server)
- **Disk space**: ~500MB (includes embeddings model)
- **Memory**: ~200MB (MCP server runtime)

## Next Steps

- **[Architecture](../explanation/architecture)** - Understand how it works
- **[Standards](../reference/standards)** - Browse universal standards
- **[Workflows](../reference/workflows)** - Start using workflows

