# MCP Debugging by Environment

**Status:** Research in Progress  
**Started:** 2025-10-24  
**Purpose:** Document IDE-specific patterns for debugging MCP server issues

---

## Overview

This document collects environment-specific information for debugging MCP servers across different AI agent platforms. As patterns emerge, this will inform future standards or documentation structure.

### Complexity Dimensions

**The installation challenge has multiple dimensions:**

1. **IDE/Platform** - Which tool (Cursor, Claude Desktop, Cline, Windsurf, Aider, etc.)
2. **Usage Mode** - How the agent operates:
   - Chat-based (back-and-forth with user)
   - Autonomous (runs tasks with minimal interaction)
   - Composer-style (multi-file editing sessions)
   - Inline (direct code suggestions)
3. **Capabilities** - What the agent can do:
   - Terminal access (can run shell commands) vs. no terminal
   - Direct file system access vs. tool-mediated
   - Native MCP support vs. extension-based
   - Synchronous vs. asynchronous execution
4. **Multi-agent Support**:
   - Single agent only (most tools)
   - Sub-agent capable (Claude Desktop, potentially others)

**Examples of edge cases:**
- **Cursor** - Has chat mode, Composer mode, inline suggestions - which one installs Agent OS?
- **Claude Desktop** - Pure MCP, no terminal - needs different approach (maybe MCP tool for installation?)
- **Cline** - Has autonomous mode - could potentially run installation script directly
- **Aider** - Command-line first, might need different instructions entirely

**This creates a matrix, not a list:**

| IDE | Chat Mode | Autonomous | Terminal | MCP | Installation Approach |
|-----|-----------|------------|----------|-----|----------------------|
| Cursor | ✅ | ⚠️ Limited | ✅ | ✅ | Step-by-step OR script |
| Claude Desktop | ✅ | ❌ | ❌ | ✅ | MCP-driven? |
| Cline | ✅ | ✅ | ✅ | ⚠️ TBD | Autonomous script run? |
| Windsurf | ✅ | ⚠️ TBD | ✅ | ⚠️ TBD | TBD |
| Aider | CLI | ✅ | ✅ | ❌ | CLI-first approach |

**Key Question for Installation Redesign:**
Should the user specify both IDE AND usage mode in the prompt?

**Examples:**
```
Install Agent OS from github.com/honeyhiveai/praxis-os for Cursor (chat mode)
Install Agent OS from github.com/honeyhiveai/praxis-os for Cursor (autonomous mode)
Install Agent OS from github.com/honeyhiveai/praxis-os for Claude Desktop (MCP-only)
Install Agent OS from github.com/honeyhiveai/praxis-os for Cline (autonomous)
```

Or should the installation instructions adapt based on detected capabilities?

### Critical Discovery: Multi-Agent Configurations

**From this very conversation (2025-10-24):**

The user revealed a complex setup that breaks the simple "one IDE = one agent" mental model:

**Current Setup:**
- **Primary Agent:** Cursor IDE (Claude Sonnet 4.5) - this conversation
- **Secondary Agent:** Cline VS Code extension, installed IN Cursor
- **MCP Server:** Single instance, dual transport (stdio + HTTP)
- **Connectivity:**
  - Cursor connects via stdio (primary, launches MCP server)
  - Cline connects via HTTP (secondary, uses existing server)
  - Both agents access the SAME MCP server simultaneously

**But also possible:**
- **Primary Agent:** Cline in pure VS Code (not Cursor)
- **MCP Server:** Launched by VS Code for Cline
- Different `mcp.json` configuration entirely

**This means:**

1. **Installation is IDE-specific, not agent-specific**
   - The installation must configure mcp.json for the HOST IDE (Cursor or VS Code)
   - Not for the agent tool (Cursor AI vs Cline)

2. **Multiple agents can share one MCP server**
   - Cursor launches MCP with dual transport
   - Cline connects to the same instance via HTTP
   - No need to install Agent OS twice

3. **The installation prompt must specify the PRIMARY IDE:**
   ```
   Install Agent OS from github.com/honeyhiveai/praxis-os for Cursor
   ```
   - This configures `.cursor/mcp.json` 
   - Enables stdio transport (primary)
   - Optionally enables HTTP transport (for secondary agents like Cline)

4. **Secondary agent setup is different:**
   - If Cline is PRIMARY (in VS Code): Install normally for VS Code
   - If Cline is SECONDARY (in Cursor): Just configure HTTP endpoint, no install needed

**Installation Matrix (Updated):**

| Primary IDE | MCP Config File | Primary Transport | Secondary Agents | Installation Approach |
|-------------|-----------------|-------------------|------------------|-----------------------|
| Cursor | `.cursor/mcp.json` | stdio | Cline (HTTP) | Standard install + HTTP transport |
| VS Code | `.vscode/mcp.json` | stdio | ??? | Standard install |
| Claude Desktop | `claude_desktop_config.json` | stdio | N/A | MCP-only install |

**Real-World Multi-Agent Use Case (From User):**

**Primary Agent:** Cursor (chat/composer mode)
**Secondary Agent:** Cline (autonomous QC)
**Tertiary Agent:** Claude Code extension (additional validation)

> "I use Cursor and Cline to both talk to Claude 4.5 Sonnet and QC each other's work"

All three agents:
- Access the SAME MCP server → shared knowledge, shared RAG index
- Query the same standards → consistent behavior
- See the same workflow state
- Use same LLM (Claude Sonnet 4.5) → eliminates model capability differences

**Different interaction modes:**
- **Cursor**: Primary development (chat, composer, inline)
- **Cline**: Autonomous QC tasks, testing, validation
- **Claude Code**: Additional review/validation layer

**Quality checking workflow:**
- Cursor implements feature
- Cline runs autonomous validation
- Claude Code does additional review
- All three agents can see each other's work via shared MCP state

**This validates the multi-agent architecture:**
- ✅ One MCP server can serve multiple agents simultaneously
- ✅ HTTP transport enables flexible agent combinations
- ✅ Shared knowledge base creates consistency across agents
- ✅ Different agent UIs/modes become complementary tools, not competitors

**Installation implications:**
- Default should probably enable HTTP transport (it's not just an edge case!)
- Documentation should promote multi-agent workflows, not treat them as advanced
- Installation prompt could be:
  ```
  Install Agent OS from github.com/honeyhiveai/praxis-os for Cursor
  
  ✅ Installed for Cursor IDE (primary)
  ❓ Enable multi-agent access? (Recommended) [Y/n]
     → Allows Cline, Windsurf, or other agents to connect via HTTP
  ```

**Existing Multi-Agent Infrastructure:**

We already have `.praxis-os/bin/update-cline-mcp.py` which:
- Reads dynamic port from `.praxis-os/.mcp_server_state.json`
- Finds Cline config in both VSCode and Cursor locations
- Updates `cline_mcp_settings.json` with HTTP connection
- Uses `"type": "streamableHttp"` (critical - without it, defaults to deprecated SSE)
- Includes `alwaysAllow` list for common tools

**Key Insight: Cline MCP Integration Varies by Mode**

| Mode | Primary IDE | Cline Transport | Config Location | Setup Method |
|------|-------------|-----------------|-----------------|--------------|
| Cline as Secondary | Cursor | HTTP | `~/Library/.../Cursor/.../cline_mcp_settings.json` | Run `update-cline-mcp.py` |
| Cline as Primary | VS Code | stdio | VS Code's MCP config | Standard install |

**Why is the port dynamic?**

**Critical reason:** Multiple Cursor windows/projects can run simultaneously, each with their own MCP server instance.

- User opens Project A in Cursor Window 1 → MCP server allocates port 4242
- User opens Project B in Cursor Window 2 → MCP server needs different port → allocates 4243
- User opens Project C in Cursor Window 3 → allocates 4244
- etc.

**Port allocation mechanism:**
- Range: 4242-5242 (1000 ports available)
- `PortManager.find_available_port()` finds next available port in range
- Validates availability via actual socket binding
- Writes allocated port to `.praxis-os/.mcp_server_state.json`

**Why this matters for installation:**

1. **Cannot hardcode HTTP port in mcp.json** 
   - Each project/window gets different port at runtime
   - Port is unknown until MCP server starts

2. **Secondary agents must read the state file**
   - `update-cline-mcp.py` reads `.praxis-os/.mcp_server_state.json`
   - Gets current port dynamically
   - Updates Cline config with current port

3. **Installation can't configure HTTP endpoint upfront**
   - Can only configure stdio transport in mcp.json
   - HTTP endpoint discovery happens after server starts
   - Secondary agent setup is a separate step (after first server launch)

**This means:**
- The installation needs to detect: "Is this PRIMARY or SECONDARY agent setup?"
- For PRIMARY: Configure stdio in IDE's native mcp.json (port allocated at runtime)
- For SECONDARY: Run the update script to configure HTTP connection (reads dynamic port from state file)
- The update script dynamically reads port (because HTTP port is allocated at runtime)
- **Installation instructions must explain: Launch primary IDE first, then configure secondary agents**

**Installation Scope Clarification (2025-10-24):**

1. **Secondary agent setup is OUT OF SCOPE for installation**
   - It's a documented feature/workflow (post-installation)
   - Uses `update-cline-mcp.py` script
   - Requires primary IDE to be running first

2. **Primary installation MUST handle:**
   - Agent + IDE combination detection
   - Correct mcp.json location for that IDE
   - Enable dual transport in mcp.json (for future secondary agents)

3. **The Installation Matrix (What We Need To Confirm):**

| Agent | IDE | MCP Config Location | Notes |
|-------|-----|---------------------|-------|
| Cursor Agent | Cursor IDE | `.cursor/mcp.json` | Built-in agent, only works with Cursor |
| Cline | VS Code | `.vscode/mcp.json` (?) | Extension - **CONFIRM** |
| Copilot | VS Code | `.vscode/mcp.json` (?) | Extension - **CONFIRM** |
| Cline | Cursor | N/A | Secondary agent case (out of scope) |
| Windsurf | ??? | ??? | **RESEARCH NEEDED** |
| Aider | CLI | N/A (?) | Command-line tool - different approach? |
| Claude Desktop | Standalone | `~/Library/.../claude_desktop_config.json` | **CONFIRM PATH** |

**Key Unknowns:**
- Do Cline, Copilot, etc. always use VS Code's mcp.json?
- What about VS Code forks (VSCodium, etc.)?
- Does Windsurf have its own IDE or is it an extension?
- How does Claude Desktop handle MCP config?
- Are there other agent+IDE combinations we're missing?

**Installation Design Decision:**
- Installation prompt should ask for **PRIMARY IDE** (not agent)
- Examples:
  - "Install Agent OS for Cursor" → `.cursor/mcp.json`
  - "Install Agent OS for VS Code" → `.vscode/mcp.json` (works for Cline, Copilot, etc.)
  - "Install Agent OS for Claude Desktop" → `claude_desktop_config.json`

**Multi-Project Complexity (2025-10-24):**

**Problem: Not all IDEs support per-project MCP configuration**

| IDE/Agent | Config Scope | Config Location | Multi-Project Support | Installation Complexity |
|-----------|-------------|-----------------|----------------------|------------------------|
| **Cursor** | ✅ Per-project | `.cursor/mcp.json` | ✅ Each project independent | ⭐ Easy |
| **Copilot** | ✅ Per-project | `.vscode/mcp.json` (?) | ✅ Each project independent | ⭐ Easy |
| **Claude Code Extension** | ✅ Per-project | `.mcp.json` | ✅ Each project independent | ⭐ Easy |
| VS Code + Cline | Global | `~/Library/.../cline_mcp_settings.json` | ⚠️ Needs testing | ⭐⭐ Medium |
| Claude Desktop App | ❌ Global | `~/Library/.../claude_desktop_config.json` | ❌ Single config for all projects | ⭐⭐⭐ Hard |
| Windsurf | ❌ Global | ??? | ❌ Single config for all projects | ⭐⭐⭐ Hard |

**The Global Config Problem:**

When Claude Desktop or Windsurf uses a SINGLE global config:
- User has Project A with Agent OS installed
- User has Project B with Agent OS installed
- User has Project C WITHOUT Agent OS
- **All three projects would need to be listed in ONE config file**

**Example broken scenario:**
```json
// claude_desktop_config.json (GLOBAL)
{
  "mcpServers": {
    "agent-os-rag": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/project-a/.praxis-os"  // Which project???
    }
  }
}
```

**The problem:**
- Can only point to ONE project at a time
- Switching projects requires manually editing global config
- Or... need multiple named servers (agent-os-project-a, agent-os-project-b, etc.)
- Or... don't support these IDEs until they fix their architecture

**Cline Multi-Project Status:**
- Uses global config: `~/Library/.../cline_mcp_settings.json`
- `update-cline-mcp.py` hasn't been tested with multiple projects
- May need to support multiple named servers in same config
- HTTP port discovery works per-project (reads local `.praxis-os/.mcp_server_state.json`)

**Installation Design Implications:**

**✅ Tier 1: Full Support (v1 Priority)**
1. **Cursor** 
   - Per-project config: `.cursor/mcp.json`
   - Multi-project works perfectly
   - No special handling needed
   - **YOU USE THIS - Full validation**

2. **Copilot (VS Code)**
   - Per-project config: `.vscode/mcp.json` (confirm exact path)
   - Multi-project works perfectly
   - Standard VS Code MCP integration
   - **Okta friend uses this - External validation**

3. **Claude Code Extension** 🆕
   - Per-project config: `.mcp.json` (root of project)
   - Multi-project works perfectly
   - Uses `claude mcp add --project` CLI
   - Works in VS Code extension mode (confirmed by conversation)
   - **Friend #2 wants this - Additional validation**
   - **Note:** Unclear if same `.mcp.json` works in terminal/desktop app modes

**⚠️ Tier 2: Secondary/Tertiary Agents (Post-Install Documentation)**
4. **Cline Extension** (as secondary agent)
   - As secondary agent in Cursor: Works via HTTP
   - As secondary agent in VS Code: Works via HTTP
   - Setup via `update-cline-mcp.py` after primary installation
   - **USER VALIDATED** (used for QC workflow)

**❌ Tier 3: Out of Scope (v1)**
5. **Claude Desktop (standalone app)**
   - Global config, can't auto-install safely
   - Multiple usage modes (terminal, extension, app) complicate support
   - Wait for per-project config support
   
6. **Windsurf**
   - Global config, can't auto-install safely  
   - **Attempted 2 hours, couldn't get working (2025-10-24)**
   - Low priority - revisit only if users specifically request
   - No manual docs until proven working

**V1 Installation Scope:**
- **Automated Primary Installations:** Cursor, VS Code/Copilot, Claude Code extension
- **Documented Secondary Agent Setup:** Cline (via HTTP)
- **Out of Scope:** Claude Desktop app, Windsurf, terminal-based tools

**Key Insight:**
Installation = PRIMARY IDE/extension setup (launches MCP server)
Secondary agents = POST-INSTALL connections (use existing server via HTTP)

**Config File Locations:**

| Agent/IDE | MCP Config | Instructions/Rules | Other Config |
|-----------|------------|-------------------|--------------|
| **Cursor** | `.cursor/mcp.json` | `.cursorrules` | - |
| **VS Code/Copilot** | `.vscode/mcp.json` | ? | ? |
| **Claude Code** | `.mcp.json` | `CLAUDE.md` | `.claude/settings.json` |
| **Cline** | `~/Library/.../cline_mcp_settings.json` | ? | ? |

**Claude Code Configuration Files:**
1. `.mcp.json` - MCP servers (stdio/http transport) ← **Our script handles this**
2. `CLAUDE.md` - Natural language instructions (like `.cursorrules`) ← **Need to consider**
3. `.claude/settings.json` - Structured config (permissions, hooks, env vars) ← **Need to research**

**External User Requests (2025-10-24):**
- Friend #1: VS Code/Copilot support (Okta) → ✅ Planned for v1
- Friend #2: Claude Code extension support → ✅ Script created!

**New Script Created:**
- `.praxis-os/bin/configure-claude-code-mcp.py`
- Configures `.mcp.json` in project root
- Sets up stdio transport (Claude Code as PRIMARY agent)
- Enables dual transport for potential secondary agents
- Similar pattern to `update-cline-mcp.py` but for different config file

**Claude Code Usage Modes:**
1. **As extension in VS Code/Cursor** → Already supported as secondary/tertiary agent via HTTP
2. **As Claude Desktop app** → Global config, problematic
3. **As terminal tool** → Different paradigm

**Questions for Friend #2:**
- Which mode do they want to use? (Extension? App? Terminal?)
- Do they want it as PRIMARY agent (launches MCP server) or SECONDARY (connects to existing)?
- If PRIMARY, which IDE/mode?

**Next Steps Before Designing Installation:**
- [ ] Clarify Friend #2's Claude Code usage mode
- [ ] Test Cline multi-project setup (2 projects open, both with Agent OS)
- [ ] Confirm Copilot exact mcp.json path for VS Code
- [ ] Decide: Do we need to support Claude Desktop app mode?
- [ ] Consider: Should installation detect and warn about global config IDEs?

---

## Cursor IDE

### MCP Log Locations

Cursor stores MCP logs in a specific directory structure, organized by session and window.

**Default Log Directories by OS:**
- **macOS:** `~/Library/Application Support/Cursor/logs/`
- **Windows:** `%AppData%/Cursor/logs`
- **Linux:** `~/.config/Cursor/logs`

**Detailed File Structure:**

Inside the logs directory:
1. Session folders named with timestamp format: `YYYYMMDDTHHMMSS` (e.g., `20250313T140544`)
2. Each session folder contains `window[N]` folders where [N] is the window number (e.g., `window1`)
3. Primary MCP log location: `window[N]/exthost/anysphere.cursor-always-local/Cursor MCP.log`

**Example full path (macOS):**
```
~/Library/Application Support/Cursor/logs/20250313T140544/window1/exthost/anysphere.cursor-always-local/Cursor MCP.log
```

**Other Related Logs:**
- File sync and retrieval logs can be found in the same session and window folders
- Multiple log files may exist in the `exthost` directory

### Finding Your Session Logs

```bash
# Navigate to logs directory
cd ~/Library/Application\ Support/Cursor/logs/

# List sessions (newest first)
ls -lt

# Find MCP logs in a specific session
find 20250313T140544 -name "*MCP.log"
```

---

## Claude Desktop

**Status:** Not yet documented

### MCP Log Locations
TODO: Research and document

### Debugging Techniques
TODO: Research and document

---

## Cline (VS Code Extension)

**Status:** Not yet documented

### MCP Log Locations
TODO: Research and document

### Debugging Techniques
TODO: Research and document

---

## Windsurf

**Status:** Not yet documented

### MCP Log Locations
TODO: Research and document

### Debugging Techniques
TODO: Research and document

---

## Common Patterns (Emerging)

*This section will be populated as patterns emerge across environments*

### Similarities
- TBD

### Differences
- TBD

### Best Practices
- TBD

---

## Next Steps

- [ ] Document Claude Desktop log locations
- [ ] Document Cline log locations
- [ ] Document Windsurf log locations
- [ ] Test MCP debugging workflows per environment
- [ ] Identify common debugging patterns
- [ ] Determine if this should become a standard or reference doc
- [ ] Consider if environment-specific guides are needed

---

## Notes

- This is exploratory research - structure may change as patterns emerge
- Focus on information that helps users troubleshoot MCP server issues
- Keep user-facing (not implementation details)
- Consider maintenance burden of environment-specific docs

### Meta-Observation: Context Compaction & Orientation

**Interesting behavior observed during this session:**

When this conversation started, context had been compacted from a previous session. The AI agent automatically:
1. Detected incomplete orientation (via `.cursorrules` mandatory check)
2. Ran `search_standards("orientation bootstrap queries mandatory ten queries")`
3. Executed all 10 mandatory bootstrap queries
4. Replied "✅ Oriented. Ready."
5. Then proceeded with the user's question

**This demonstrates:**
- ✅ **Context compaction works** - Agent didn't have prior session knowledge but recovered automatically
- ✅ **Orientation is enforced** - `.cursorrules` gate prevents work without proper behavioral grounding
- ✅ **RAG-driven behavior** - Querying 10 standards loads behavioral patterns for the session
- ✅ **Self-correcting system** - No user intervention needed to restore proper agent behavior

**Implications for environment-specific debugging:**
- Agents may need to re-orient after context compaction
- Behavioral patterns must be loaded via RAG, not assumed from prior sessions
- This is why standards are indexed and queried, not memorized
- Cross-session debugging might require re-establishing agent state

This observation might inform how we document debugging workflows that span multiple sessions or different agent instances.

