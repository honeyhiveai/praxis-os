# Multi-Agent Architecture - Primary vs Secondary Agents

**Keywords for search**: primary agent, secondary agent, MCP server ownership, dual transport, stdio vs HTTP, multi-agent workflow, Cursor primary Cline secondary, agent collaboration, MCP connection types, server lifecycle management, auto-discovery, helper scripts for agents, when to use primary vs secondary

---

## 🚨 TL;DR - Multi-Agent Architecture Quick Reference

**Core Principle:** One primary agent owns the MCP server lifecycle (stdio), multiple secondary agents connect via HTTP. This enables multi-agent collaboration without conflicts.

**Key Distinctions:**

1. **Primary Agent** - Owns MCP server lifecycle
   - Starts/stops the server
   - Native stdio connection
   - Configured via `.cursor/mcp.json` (or equivalent)
   - Example: Cursor as your main IDE

2. **Secondary Agent** - Connects to existing server
   - Depends on primary's running server
   - HTTP connection (Streamable HTTP protocol)
   - Auto-discovers via `.praxis-os/.mcp_server_state.json`
   - Example: Cline connecting to Cursor's MCP server

3. **Helper Scripts** - Only for secondary agent setup
   - `configure-claude-code-mcp.py` - Configures Claude Code as secondary
   - `update-cline-mcp.py` - Configures Cline as secondary
   - Located in `.praxis-os/scripts/` (copied during installation)
   - Read dynamic port from state file

**When to Use:**
- **Most users:** Primary mode only (simplest)
- **Advanced workflows:** Primary + secondary for multi-agent collaboration
- **Testing/debugging:** Secondary agents to validate different perspectives

**Architecture:**
```
Primary Agent (Cursor)
    ├─ Owns MCP server (stdio connection)
    └─ Enables HTTP endpoint: http://localhost:4242/mcp
        ├─ Secondary Agent (Cline) connects via HTTP
        └─ Secondary Agent (Claude Code) connects via HTTP
```

---

## ❓ Questions This Answers

1. What is the difference between primary and secondary agent mode?
2. When should I use primary vs secondary agent setup?
3. How does Cursor connect to the MCP server differently than Cline?
4. What is dual-transport mode in the MCP server?
5. Why do secondary agents need helper scripts?
6. Where do helper scripts live after installation?
7. How do secondary agents discover the MCP server port?
8. What is the `.mcp_server_state.json` file for?
9. Can I run multiple agents simultaneously?
10. Which agent should be the primary agent?
11. How does stdio differ from HTTP for MCP connections?
12. What happens if the primary agent stops?
13. Why not make all agents primary?
14. How does auto-discovery work for secondary agents?
15. What is the port range for MCP servers?
16. Can I have multiple praxis-os projects running?
17. How do helper scripts read the dynamic port?
18. Why are helper scripts only for secondary agents?
19. What transport type does Cline use for secondary mode?
20. How does the MCP server handle concurrent connections?

---

## 🎯 Purpose

Define the architecture and distinctions between primary and secondary agent modes in prAxIs OS multi-agent workflows. This enables contributors to understand, implement, and test multi-agent collaboration features correctly.

---

## ❌ The Problem - Without This Understanding

**For framework developers:**
- ❌ Confusion about when helper scripts are needed
- ❌ Incorrect installation instructions (copying scripts unnecessarily)
- ❌ Poor testing (not validating both primary and secondary modes)
- ❌ Documentation inconsistency (mixing primary/secondary concepts)

**For contributors:**
- ❌ Breaking changes to secondary agent setup
- ❌ Helper scripts in wrong locations
- ❌ Testing only primary mode (missing secondary bugs)

**For users (if we ship bad docs):**
- ❌ Complex setup where simple would work
- ❌ Manual steps that should be automatic
- ❌ Broken secondary agent configuration

---

## ✅ The Standard - Multi-Agent Architecture

### Primary Agent (Server Owner)

**Definition:** The agent that starts and manages the MCP server lifecycle.

**Characteristics:**
- **Lifecycle:** Starts, stops, restarts the MCP server
- **Connection:** Native/direct (stdio transport)
- **Configuration:** IDE-specific MCP config (e.g., `.cursor/mcp.json`)
- **Transport:** `stdio` (standard input/output)
- **Independence:** Self-sufficient, doesn't depend on other agents
- **Server Mode:** Starts with `--transport dual` for multi-agent support

**Configuration Example (Cursor):**
```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "transport": "stdio"
    }
  }
}
```

**When to Use:**
- ✅ Your main IDE/editor
- ✅ Agent you use most frequently
- ✅ Agent that's always running during development

---

### Secondary Agent (HTTP Client)

**Definition:** An agent that connects to an existing MCP server via HTTP.

**Characteristics:**
- **Lifecycle:** Depends on primary agent being running
- **Connection:** HTTP (Streamable HTTP protocol)
- **Configuration:** HTTP URL to primary's server
- **Transport:** `streamableHttp` or `http`
- **Independence:** Requires primary agent to be active
- **Auto-Discovery:** Reads port from `.praxis-os/.mcp_server_state.json`

**Configuration Example (Cline):**
```json
{
  "mcpServers": {
    "praxis-os-rag": {
      "url": "http://127.0.0.1:4242/mcp",
      "transport": "streamableHttp"
    }
  }
}
```

**When to Use:**
- ✅ Additional agents for different perspectives
- ✅ Testing/validation workflows
- ✅ Specialized agents (design review, security audit)
- ❌ NOT for primary development (use primary mode)

---

### Dual-Transport Mode

**What It Is:** MCP server running with both stdio (for primary) and HTTP (for secondary) transports simultaneously.

**Enabled By:** `--transport dual` argument when starting MCP server

**Port Allocation:**
- Dynamic range: `4242-5242`
- Auto-allocated to avoid conflicts
- Written to `.praxis-os/.mcp_server_state.json`

**State File Example:**
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

**Benefits:**
- ✅ Multiple agents access same MCP server
- ✅ Shared workflow state across agents
- ✅ Zero-conflict multi-project support
- ✅ No manual port configuration

---

### Helper Scripts (Secondary Setup Only)

**Purpose:** Automate HTTP connection configuration for secondary agents.

**Scripts:**
1. **`configure-claude-code-mcp.py`** - Sets up Claude Code as secondary agent
2. **`update-cline-mcp.py`** - Sets up Cline as secondary agent

**Location After Installation:**
- **Source:** `scripts/` (framework repository, tracked in git)
- **Installed:** `.praxis-os/scripts/` (copied during Phase 1 installation)

**What They Do:**
1. Read `.praxis-os/.mcp_server_state.json` (discovers dynamic port)
2. Generate correct HTTP URL (`http://127.0.0.1:<PORT>/mcp`)
3. Update agent-specific config file:
   - Cline: `cline_mcp_settings.json`
   - Claude Code: `.mcp.json` (project-local) and `.claude/settings.local.json`
4. Set correct transport type (`streamableHttp`)

**Usage (from consumer project):**
```bash
# Cline setup
python .praxis-os/scripts/update-cline-mcp.py

# Claude Code setup
python .praxis-os/scripts/configure-claude-code-mcp.py
```

**Why Only Secondary Agents Need Helpers:**
- Primary agents start the server directly (no discovery needed)
- Secondary agents connect to running server (need dynamic port)
- Helpers automate: read state file → generate config → write to agent config

---

## 📋 Checklist - Multi-Agent Implementation

### When Implementing Primary Agent Support

- [ ] Create agent-specific installation guide
- [ ] Document MCP config file location (e.g., `.cursor/mcp.json`)
- [ ] Include `--transport dual` flag for multi-agent support
- [ ] Verify stdio connection works
- [ ] Test server lifecycle (start, stop, restart)
- [ ] Confirm state file is written on startup

### When Implementing Secondary Agent Support

- [ ] Create helper script in `scripts/` directory
- [ ] Helper reads `.praxis-os/.mcp_server_state.json`
- [ ] Helper finds agent-specific config file location
- [ ] Helper writes correct HTTP URL and transport type
- [ ] Test auto-discovery when primary agent running
- [ ] Test error handling when primary agent not running
- [ ] Document manual setup as fallback (Option B)
- [ ] Update agent integration guide

### When Testing Multi-Agent Setup

- [ ] Test primary agent alone (stdio only)
- [ ] Test primary + secondary (dual transport)
- [ ] Test multiple secondaries simultaneously
- [ ] Test secondary connection when primary stops
- [ ] Test helper script with various port allocations
- [ ] Test multi-project scenario (different ports)
- [ ] Verify workflow state shared across agents

### When Writing Documentation

- [ ] Distinguish primary vs secondary clearly
- [ ] Show when helper scripts are needed (secondary only)
- [ ] Reference `.praxis-os/scripts/` not `.praxis-os/bin/`
- [ ] Explain auto-discovery mechanism
- [ ] Include troubleshooting for connection failures
- [ ] Emphasize: most users only need primary mode

---

## 💡 Examples - Real-World Scenarios

### Example 1: Simple Setup (Primary Only)

**User:** Python developer using Cursor as main IDE

**Setup:**
- Cursor: Primary agent (owns MCP server)
- MCP server: stdio connection
- No helper scripts needed

**Configuration:**
```json
// .cursor/mcp.json
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server"],
      "transport": "stdio"
    }
  }
}
```

**Result:** Simple, no complexity, works perfectly for single-agent workflow.

---

### Example 2: Multi-Agent Workflow (Primary + Secondary)

**User:** Team lead using Cursor + Cline for code review

**Setup:**
- Cursor: Primary agent (main development)
- Cline: Secondary agent (code review perspective)
- MCP server: dual transport mode

**Configuration:**
```json
// .cursor/mcp.json (primary)
{
  "mcpServers": {
    "praxis-os-rag": {
      "command": "${workspaceFolder}/.praxis-os/venv/bin/python",
      "args": ["-m", "mcp_server", "--transport", "dual"],
      "transport": "stdio"
    }
  }
}

// cline_mcp_settings.json (secondary, auto-generated)
{
  "mcpServers": {
    "praxis-os-rag": {
      "url": "http://127.0.0.1:4242/mcp",
      "transport": "streamableHttp"
    }
  }
}
```

**Workflow:**
1. Start Cursor (primary starts MCP server, allocates port 4242)
2. Run `python .praxis-os/scripts/update-cline-mcp.py` (auto-discovers port)
3. Start Cline (connects via HTTP to Cursor's server)
4. Both agents share same workflow state and MCP tools

**Result:** Seamless collaboration, no port conflicts, shared context.

---

### Example 3: Testing Secondary Agent Integration

**Developer:** Contributing to praxis-os, testing Cline integration

**Testing Flow:**
```bash
# 1. Start primary agent (Cursor with dual transport)
# Cursor starts automatically when IDE opens

# 2. Verify state file
cat .praxis-os/.mcp_server_state.json
# {"transport": "dual", "url": "http://127.0.0.1:4242/mcp", ...}

# 3. Test helper script
python .praxis-os/scripts/update-cline-mcp.py

# 4. Verify Cline config generated
cat ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/cline_mcp_settings.json

# 5. Start Cline, test MCP tools
# Query: "search standards for multi-agent architecture"

# 6. Verify both agents access same server
# Check both agents see same workflow state
```

**What To Validate:**
- [ ] Helper script finds state file
- [ ] Helper script reads correct port
- [ ] Helper script writes correct config
- [ ] Cline connects successfully
- [ ] Both agents share workflow state
- [ ] Error handling when primary stops

---

## 🚫 Anti-Patterns - Common Mistakes

### Anti-Pattern 1: Making All Agents Primary

**Wrong:**
```
User has 3 agents configured, all as primary:
- Cursor: stdio to MCP server (port 4242)
- Cline: stdio to MCP server (port conflict!)
- Claude Code: stdio to MCP server (port conflict!)
```

**Problem:** Each agent tries to start its own MCP server, port conflicts, no shared state

**Right:**
```
- Cursor: Primary (stdio, owns server)
- Cline: Secondary (HTTP to Cursor's server)
- Claude Code: Secondary (HTTP to Cursor's server)
```

---

### Anti-Pattern 2: Copying Helper Scripts to `.praxis-os/bin/`

**Wrong:**
```bash
# Installation docs say:
cp .praxis-os/scripts/update-cline-mcp.py .praxis-os/bin/
python .praxis-os/bin/update-cline-mcp.py
```

**Problem:** Unnecessary copy step, creates ad-hoc directory, not following dogfooding model

**Right:**
```bash
# Installation docs say:
python .praxis-os/scripts/update-cline-mcp.py
```

**Why:** Helper scripts already copied to `.praxis-os/scripts/` in Phase 1 installation

---

### Anti-Pattern 3: Hardcoding Port in Documentation

**Wrong:**
```json
// Documentation example
{
  "url": "http://127.0.0.1:4242/mcp",  // ❌ Hardcoded port
  "transport": "streamableHttp"
}
```

**Problem:** Port is dynamically allocated, might be 4243, 4244, etc.

**Right:**
```bash
# Documentation says: Use helper script
python .praxis-os/scripts/update-cline-mcp.py
# Script reads actual port from state file
```

**Alternative:** If showing manual setup, say:
```json
{
  "url": "http://127.0.0.1:<PORT>/mcp",  // Get <PORT> from .mcp_server_state.json
  "transport": "streamableHttp"
}
```

---

### Anti-Pattern 4: Testing Only Primary Mode

**Wrong:**
```python
# Test suite only tests:
def test_mcp_server_stdio():
    """Test MCP server with stdio transport"""
    # Only tests primary agent mode
```

**Problem:** Misses bugs in HTTP transport, auto-discovery, helper scripts

**Right:**
```python
def test_mcp_server_stdio():
    """Test primary agent (stdio transport)"""
    # Test primary mode
    
def test_mcp_server_dual_transport():
    """Test primary + secondary (dual transport)"""
    # Start server with --transport dual
    # Verify HTTP endpoint works
    # Test secondary agent connection
    
def test_helper_script_auto_discovery():
    """Test secondary helper script discovers port"""
    # Start server, write state file
    # Run helper script
    # Verify config generated with correct port
```

---

### Anti-Pattern 5: Over-Promoting Secondary Mode

**Wrong:**
```markdown
# Installation docs
All users should set up both Cursor and Cline for maximum productivity!

Steps:
1. Install praxis-os
2. Configure Cursor as primary
3. Configure Cline as secondary
4. Configure Claude Code as secondary
5. ...
```

**Problem:** Overwhelming for simple use case, adds complexity most users don't need

**Right:**
```markdown
# Installation docs
Most users only need primary agent setup.

**Simple Setup (Recommended):**
- Configure your main IDE (e.g., Cursor) as primary agent
- Done! You're ready to use praxis-os

**Advanced: Multi-Agent Workflows (Optional)**
If you need multiple agents collaborating:
- See: Secondary Agent Setup Guide
- Use cases: Code review, testing, specialized perspectives
```

---

## 🔗 Related Standards

**Query for related patterns:**
```python
pos_search(content_type="standards", query="dual transport architecture MCP server")
pos_search(content_type="standards", query="installation helper scripts secondary agents")
pos_search(content_type="standards", query="dogfooding model source vs installed files")
pos_search(content_type="standards", query="MCP connection types stdio HTTP")
```

**Key related documents:**
- `.praxis-os/specs/completed/2025-10-11-mcp-dual-transport/` - Full dual-transport spec
- `docs/content/how-to-guides/agent-integrations/` - Agent-specific setup guides
- `.praxis-os/standards/development/dogfooding-model.md` - Why we avoid symlinks/shortcuts

---

## 🔄 Maintenance

**Update this standard when:**
- Adding support for new agent as primary/secondary
- Changing helper script locations or naming
- Modifying auto-discovery mechanism
- Adding new transport types
- Changing port allocation strategy

**Review quarterly or when:**
- Users report confusion about primary vs secondary
- New multi-agent patterns emerge
- MCP protocol evolves (new transport types)
- Helper scripts fail in edge cases

---

## ✅ Success Criteria

A contributor understands this architecture when they can:

- [ ] Explain primary vs secondary in one sentence
- [ ] Know when helper scripts are needed (secondary only)
- [ ] Find helper scripts after installation (`.praxis-os/scripts/`)
- [ ] Understand why port is dynamic (auto-allocated)
- [ ] Test both primary and secondary modes
- [ ] Write agent integration docs correctly
- [ ] Avoid over-promoting multi-agent setup
- [ ] Debug connection issues (check state file first)

---

**Last Updated:** 2025-11-01  
**Status:** Active  
**Scope:** praxis-os development (local standard, not distributed)

