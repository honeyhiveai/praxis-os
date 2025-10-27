        
    def call_tool(self, tool_name: str, args: dict):
        """Call MCP tool with auto-reconnect."""
        if not self.url:
            self.url = self.discover_server()
        
        try:
            return self._call(self.url, tool_name, args)
        except ConnectionError:
            # Server might have restarted on different port
            self.url = self.discover_server()
            return self._call(self.url, tool_name, args)
```

**Use Case:** Server restarts don't break sub-agents

---

### 3. Remote Access (Optional)

```python
# .praxis-os/config.yaml
mcp:
  allow_remote: true
  remote_host: "0.0.0.0"
  auth_token: "${MCP_AUTH_TOKEN}"
```

**Use Case:** Remote agents (cloud CI/CD, remote teams)

**Security Requirements:**
- Authentication token
- HTTPS/TLS
- Rate limiting
- IP whitelisting

---

### 4. Multi-Server Aggregation

```python
class MultiServerClient:
    """Client that aggregates tools from multiple MCP servers."""
    
    def __init__(self, servers: List[str]):
        self.servers = servers
        
    def list_all_tools(self):
        """List tools from all servers."""
        all_tools = []
        for server_url in self.servers:
            tools = self.call(server_url, "tools/list")
            all_tools.extend(tools)
        return all_tools
```

**Use Case:** Sub-agent needs tools from multiple projects

---

### 5. Port Range Configuration

```yaml
# .praxis-os/config.yaml
mcp:
  port_range:
    start: 8000
    end: 9000
```

**Use Case:** Corporate environments with firewall rules

---

## Appendix A: State File Schema

```typescript
interface MCPServerState {
  // Schema version for forward compatibility
  version: "1.0.0";
  
  // Transport mode
  transport: "dual" | "stdio" | "http";
  
  // HTTP configuration (null for stdio-only)
  port: number | null;
  host: string;
  path: string;
  url: string | null;
  
  // Process information
  pid: number;
  started_at: string;  // ISO 8601 timestamp
  
  // Optional metadata
  project_root?: string;
  agent_os_version?: string;
}
```

---

## Appendix B: CLI Reference

```bash
# Agent OS MCP Server CLI

python -m mcp_server --help

Usage: python -m mcp_server [OPTIONS]

Options:
  --transport {dual,stdio,http}
      Transport mode (REQUIRED)
      
      dual:   stdio for IDE + HTTP for sub-agents (recommended)
      stdio:  IDE communication only (no sub-agents)
      http:   Network communication only (all agents via HTTP)
  
  --log-level {DEBUG,INFO,WARNING,ERROR}
      Logging verbosity (default: INFO)
  
  --help
      Show this help message

Examples:
  # Dual transport (Cursor + sub-agents)
  python -m mcp_server --transport dual
  
  # HTTP only (standalone server)
  python -m mcp_server --transport http
  
  # stdio only (IDE integration, no sub-agents)
  python -m mcp_server --transport stdio
  
  # Debug logging
  python -m mcp_server --transport dual --log-level DEBUG
```

---

## Appendix C: Troubleshooting

### Problem: "No available ports in range"

**Symptom:**
```
RuntimeError: No available ports in range 4242-5242
```

**Cause:** 1000 MCP servers already running (unlikely)

**Solution:**
```bash
# Find all MCP servers
ps aux | grep "mcp_server"

# Kill old servers
pkill -f "mcp_server"
```

---

### Problem: "MCP server not responding"

**Symptom:** Sub-agent can't connect to HTTP endpoint

**Debug Steps:**
```bash
# 1. Check state file exists
cat .praxis-os/.mcp_server_state.json

# 2. Check server is running
ps aux | grep mcp_server

# 3. Test HTTP endpoint manually
curl -X POST http://127.0.0.1:4243/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# 4. Check server logs
# (logs location depends on how server was started)
```

---

### Problem: "State file is stale"

**Symptom:** State file exists but server not running

**Cause:** Server crashed without cleanup

**Solution:**
```bash
# Delete stale state file
rm .praxis-os/.mcp_server_state.json

# Restart IDE/server
```

---

### Problem: "Port already in use"

**Symptom:** Server won't start, port allocation fails

**Cause:** Another process using port 4242-5242

**Solution:**
```bash
# Find what's using the ports
lsof -i :4242-4244

# Kill specific process or choose different port range
```

---

## Conclusion

This dual-transport architecture provides:

✅ **Seamless IDE integration** (stdio)  
✅ **Sub-agent support** (HTTP)  
✅ **Multi-project isolation** (auto port allocation)  
✅ **Zero conflicts** (dynamic port management)  
✅ **Simple discovery** (state file)  
✅ **IDE agnostic** (works with Cursor, Windsurf, etc.)

The design prioritizes:
- **Explicit configuration** over magic behavior
- **Automatic conflict resolution** over manual configuration
- **Project isolation** over shared state
- **Simple debugging** over complex abstractions

Ready for implementation and testing.


</file_content>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
mcp_server/models/config.py
mcp_server/__main__.py
.cursor/mcp.json

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
mcp_server/__main__.py
.cursor/mcp.json

# Current Time
10/11/2025, 7:18:17 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
131,034 / 200K tokens used (66%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## Thoughts on Dual-Transport Design

### What I Got Wrong

**My implementation:**
```python
# HTTP-only (WRONG)
mcp.run(transport="http", host="127.0.0.1", port=4242, path="/mcp")
```

**What the design actually needs:**
```python
# Dual transport (CORRECT)
# Main thread: stdio for IDE
# Background thread: HTTP for sub-agents
python -m mcp_server --transport dual
```

### Why Dual Transport is Brilliant

**The Real Problem:**
- **IDE needs stdio** - Cursor spawns the process and uses stdin/stdout pipes
- **Sub-agents need HTTP** - Cline/Aider run in different environments, can't use stdio

**My HTTP-only solution broke IDE communication!**

The Cursor agent correctly identified:
```
Cursor launches → stdio pipes → MCP Server
                      ↓
                  (also opens HTTP port)
                      ↓
Cline/Aider → HTTP → Same MCP Server

Both access same RAG, same state, same everything!
```

### Key Design Insights

**1. Explicit Transport Mode (CLI Flag)**
```bash
--transport dual    # stdio + HTTP (most common)
--transport stdio   # IDE only (no sub-agents)
--transport http    # All agents via HTTP
```
Better than my config-based approach - makes intent clear

**2. Automatic Port Allocation**
```python
# Try 4242, if busy try 4243, 4244, etc.
port = port_manager.find_available_port(4242)
```
Solves the multi-project conflict I didn't consider!

**3. State File for Discovery**
```json
// .praxis-os/.mcp_server_state.json
{
  "transport": "dual",
  "port": 4243,
  "url": "http://127.0.0.1:4243/mcp",
  "pid": 12345
}
```
Sub-agents just read this file - no manual config!

**4. Thread-Based Architecture**
```python
# Main thread: stdio (blocks, serves IDE)
mcp.run(transport="stdio")

# Background daemon thread: HTTP
http_thread = threading.Thread(
    target=lambda: mcp.run(transport="http", port=port),
    daemon=True
)
```
Clean separation, graceful shutdown

### What I Should Have Done

**Step 1: Ask clarifying questions**
- "Do we need stdio for IDE or is HTTP enough?"
- "How will sub-agents discover the server?"
- "What about multiple projects open?"

**Step 2: Research FastMCP's dual-transport support**
- Does it support running both simultaneously?
- What's the threading model?

**Step 3: Design before implementing**
- Think through multi-project scenarios
- Consider sub-agent discovery
- Plan state management

### The Design is Excellent

**Strengths:**
- ✅ Comprehensive problem analysis
- ✅ Clear architecture with diagrams
- ✅ Handles edge cases (port conflicts, stale state, crashes)
- ✅ Well-documented CLI interface
- ✅ Testing strategy included
- ✅ Migration path planned
- ✅ Future enhancements considered

**Minor suggestions:**
- Consider making port range configurable (already in future enhancements)
- Health check endpoint would be useful (already in future enhancements)
- Document FastMCP's threading model/safety

### What Needs Implementation

**New files needed:**
1. `mcp_server/port_manager.py` - Port allocation + state file
2. `mcp_server/transport_manager.py` - Threading orchestration
3. Update `mcp_server/__main__.py` - Add CLI args + transport selection

**My files need reverting:**
- `mcp_server/__main__.py` - Remove HTTP-only, add dual support
- `.cursor/mcp.json` - Add `--transport dual` arg
- `mcp_server/models/config.py` - Keep HTTP config but make it optional

### Critical Question

**Does FastMCP support running stdio + HTTP concurrently?**

From the README I fetched:
```python
mcp.run(transport="stdio")  # OR
mcp.run(transport="http", ...)  # OR
mcp.run(transport="sse", ...)
```

It shows OR not AND. **We need to verify FastMCP supports dual-transport before implementing.**

If FastMCP doesn't support it natively, we'd need to:
1. Create two FastMCP instances
2. Share the same tools/resources between them
3. Coordinate shutdown

### My Recommendation

**Before implementing:**
1. ✅ Verify FastMCP can run stdio + HTTP simultaneously
2. ✅ Test threading model is safe for tools
3. ✅ Confirm port binding doesn't block stdio

**Then implement:**
1. Port manager (straightforward)
2. Transport manager (needs FastMCP investigation)
3. CLI args (straightforward)
4. Testing (comprehensive in design doc)

**The design is solid. My hasty HTTP-only implementation missed the actual requirement. Let the Cursor agent implement their well-thought-out design!**
</result>
<task_progress>
- [x] Read dual-transport design document
- [x] Understood my HTTP-only mistake
- [x] Recognized dual transport is the real requirement
- [x] Analyzed design strengths and considerations
- [x] Identified FastMCP capability question
- [x] Ready to help implement proper dual-transport solution
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
read the updated design doc
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
mcp_server/project_info.py
../../../../Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
mcp_server/models/config.py
mcp_server/__main__.py
.cursor/mcp.json

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
.cursor/mcp.json
mcp_server/__main__.py
mcp_server/models/config.py
DESIGN-DOC-MCP-Dual-Transport.md

# Current Time
10/11/2025, 7:56:11 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
145,970 / 200K tokens used (73%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>DESIGN-DOC-MCP-Dual-Transport.md</path>
<task_progress>
- [x] Read original design doc
- [ ] Read updated design doc
- [ ] Understand what changed
- [ ] Provide analysis
</task_progress>
</read_file>

---

**User:**

[read_file for 'DESIGN-DOC-MCP-Dual-Transport.md'] Result:
# Design Document: MCP Server Dual-Transport Architecture

**Version:** 1.0  
**Date:** October 11, 2025  
**Status:** Design Phase  
**Authors:** Agent OS Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Goals and Non-Goals](#goals-and-non-goals)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Design](#detailed-design)
6. [Component Specifications](#component-specifications)
7. [Project Information Discovery](#project-information-discovery)
8. [Configuration](#configuration)
9. [Port Management](#port-management)
10. [State Management](#state-management)
11. [Transport Modes](#transport-modes)
12. [Multi-Project Support](#multi-project-support)
13. [Sub-Agent Integration](#sub-agent-integration)
14. [Error Handling](#error-handling)
15. [Security Considerations](#security-considerations)
16. [Testing Strategy](#testing-strategy)
17. [Migration Path](#migration-path)
18. [Future Enhancements](#future-enhancements)

---

## Executive Summary

This document describes a dual-transport architecture for the Agent OS MCP (Model Context Protocol) server that enables:

1. **Primary IDE integration** via stdio transport (Cursor, Windsurf, Claude Desktop)
2. **Sub-agent access** via HTTP transport (Cline, Aider, custom agents)
3. **Multi-project isolation** with automatic port allocation
4. **Zero-conflict deployment** across multiple Cursor windows

**Key Design Principles:**
- **Explicit transport mode** (user-controlled)
- **Automatic port allocation** (system-controlled)
- **Project isolation** (separate state per project)
- **Single venv requirement** (agent-os dependencies)

**Validation Status:** ✅ **FULLY VALIDATED AND PRODUCTION-READY**

This design has been completely validated with working code and real MCP SDK testing:
- ✅ Dual transport proven (stdio + HTTP simultaneously)
- ✅ Tool calls validated via HTTP using MCP SDK client
- ✅ Same FastMCP instance serves both transports
- ✅ Working implementation provided (see Critical Assumptions section)
- ✅ Ready for production implementation

---

## Problem Statement

### Current Limitations

1. **Single Transport Model**
   - Current implementation uses only HTTP or only stdio
   - Can't serve both IDE (stdio) and sub-agents (HTTP) simultaneously

2. **Port Conflicts**
   - Multiple Agent OS instances (different Cursor windows) conflict on port 4242
   - No mechanism to allocate different ports per project

3. **Sub-Agent Access**
   - Sub-agents (Cline, Aider) run in different environments
   - Can't import mcp_server code (different venvs)
   - Need network access to shared MCP server

4. **Venv Dependency**
   - MCP server MUST run from `.praxis-os/venv/` for:
     - RAG engine (lancedb, sentence-transformers)
     - File watchers (watchdog)
     - Markdown parsing (mistletoe)
     - Browser automation (playwright)

### Real-World Scenario

```
Developer has 3 Cursor windows open:
  - Window 1: project-a (port 4242 ❌ conflict)
  - Window 2: project-b (port 4242 ❌ conflict)
  - Window 3: project-c (port 4242 ❌ conflict)

Developer wants Cline agent in project-a:
  - Cline can't use stdio (not the IDE)
  - Cline runs in different venv (can't import mcp_server)
  - Cline needs HTTP access to project-a's MCP server
```

---

## Goals and Non-Goals

### Goals

✅ **Support dual transport**: stdio (IDE) + HTTP (sub-agents) simultaneously  
✅ **Automatic port allocation**: No conflicts across multiple projects  
✅ **Explicit transport mode**: Clear user intent in configuration  
✅ **Project isolation**: Each project has independent server + RAG + watchers  
✅ **Sub-agent discovery**: Simple mechanism for sub-agents to find server  
✅ **IDE agnostic**: Works with Cursor, Windsurf, Claude Desktop, etc.  
✅ **Zero-configuration sub-agents**: Read state file, connect automatically  

### Non-Goals

❌ **Remote/public HTTP access**: Security out of scope (localhost only)  
❌ **Load balancing**: Single server per project is sufficient  
❌ **Multi-server aggregation**: Sub-agents don't need multiple MCP servers  
❌ **Persistent state**: State file is runtime-only, not persistent  
❌ **Hot reload of transport mode**: Requires server restart  

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  IDE (Cursor, Windsurf, Claude Desktop)                         │
│                                                                  │
│  Configuration:                                                  │
│    command: .praxis-os/venv/bin/python -m mcp_server            │
│    args: ["--transport", "dual"]        ← EXPLICIT              │
│    transport: stdio                                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Launches process
                             │ (stdin/stdout pipes)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server Process (runs in .praxis-os/venv)                    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Startup Sequence                                       │  │
│  │    ├─ Parse CLI args: --transport dual                   │  │
│  │    ├─ Load config from .praxis-os/config.yaml             │  │
│  │    ├─ Initialize PortManager                             │  │
│  │    └─ Find available port (4242 → 4243 → ...)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 2. Core Components (Dependency Injection)                │  │
│  │    ├─ RAGEngine (project-specific index)                 │  │
│  │    ├─ WorkflowEngine (state management)                  │  │
│  │    ├─ FileWatchers (.praxis-os/standards/, etc.)          │  │
│  │    └─ BrowserManager (Playwright automation)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 3. Transport Layer (mode: dual)                          │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Main Thread: stdio Transport                       │  │  │
│  │  │   ├─ Read from stdin (JSON-RPC)                    │  │  │
│  │  │   ├─ Execute tool calls                            │  │  │
│  │  │   └─ Write to stdout (JSON-RPC)                    │  │  │
│  │  │   └─> Serves IDE (Cursor)                          │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                           │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ Background Thread: HTTP Transport (port 4243)      │  │  │
│  │  │   ├─ HTTP server (uvicorn/starlette)               │  │  │
│  │  │   ├─ Streamable-HTTP protocol                       │  │  │
│  │  │   └─> Serves sub-agents (Cline, Aider, etc.)       │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 4. State File Management                                 │  │
│  │    Writes: .praxis-os/.mcp_server_state.json             │  │
│  │    {                                                     │  │
│  │      "transport": "dual",                                │  │
│  │      "port": 4243,                                       │  │
│  │      "host": "127.0.0.1",                                │  │
│  │      "path": "/mcp",                                     │  │
│  │      "url": "http://127.0.0.1:4243/mcp",                │  │
│  │      "pid": 12345,                                       │  │
│  │      "started_at": "2025-10-11T10:30:00Z"               │  │
│  │    }                                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ HTTP endpoint available
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Sub-Agents (Cline, Aider, Custom)                              │
│                                                                  │
│  1. Discover server:                                            │
│     ├─ Read .praxis-os/.mcp_server_state.json                   │
│     └─ Extract: {"url": "http://127.0.0.1:4243/mcp"}           │
│                                                                  │
│  2. Connect via HTTP:                                           │
│     ├─ POST http://127.0.0.1:4243/mcp                          │
│     └─ Use Streamable-HTTP protocol                            │
│                                                                  │
│  3. Call MCP tools:                                             │
│     ├─ search_standards()                                       │
│     ├─ get_workflow_state()                                     │
│     └─ ... all same tools as IDE                               │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────┐
│ Cursor   │
│ (stdio)  │
└────┬─────┘
     │
     │ search_standards("authentication")
     ▼
┌─────────────────────────────┐
│ MCP Server                  │
│   ├─ stdio thread receives  │
│   ├─ RAG engine queries     │
│   └─ Returns results        │
└─────────────────────────────┘
     ▲
     │ search_standards("authentication")
     │
┌────┴─────┐
│ Cline    │
│ (HTTP)   │
└──────────┘

Both agents access SAME RAG index, SAME tools, SAME state!
```

---

## Detailed Design

### System Components

```
praxis-os/
├─ .praxis-os/
│  ├─ venv/                              # Required for all dependencies
│  ├─ standards/                          # Watched by file watcher
│  ├─ workflows/                          # Watched by file watcher
│  ├─ .cache/
│  │  └─ vector_index/                    # RAG index (lancedb)
│  └─ .mcp_server_state.json             # Runtime state (gitignored)
│
├─ mcp_server/
│  ├─ __main__.py                         # Entry point (MODIFIED)
│  ├─ port_manager.py                     # NEW: Port allocation + state
│  ├─ transport_manager.py                # NEW: Transport mode handling
│  ├─ config/
│  │  ├─ loader.py
│  │  └─ validator.py
│  ├─ server/
│  │  ├─ factory.py                       # Server creation
│  │  └─ tools/                           # MCP tool implementations
│  ├─ rag_engine.py                       # RAG query engine
│  ├─ workflow_engine.py                  # Workflow state management
│  └─ monitoring/
│     └─ watcher.py                       # File watching
│
└─ .cursor/
   └─ mcp.json                            # IDE configuration
```

---

## Component Specifications

### 1. PortManager (`mcp_server/port_manager.py`)

**Responsibility:** Dynamic port allocation and state file management

```python
class PortManager:
    """Manages dynamic port allocation and state persistence."""
    
    DEFAULT_PORT_START = 4242
    DEFAULT_PORT_END = 5242
    STATE_FILE_NAME = ".mcp_server_state.json"
    
    def find_available_port(self, preferred_port: int) -> int:
        """
        Find available port, trying preferred first.
        
        Algorithm:
        1. Try preferred_port (e.g., 4242)
        2. If taken, try preferred_port + 1, + 2, etc.
        3. Stop at DEFAULT_PORT_END or raise exception
        
        :param preferred_port: Port to try first
        :return: Available port number
        :raises RuntimeError: If no ports available in range
        """
        
    def write_state(
        self,
        transport: str,
        port: Optional[int],
        host: str = "127.0.0.1",
        path: str = "/mcp"
    ) -> None:
        """
        Write server state to file for sub-agents.
        
        State file format:
        {
          "transport": "dual",
          "port": 4243,
          "host": "127.0.0.1",
          "path": "/mcp",
          "url": "http://127.0.0.1:4243/mcp",
          "pid": 12345,
          "started_at": "2025-10-11T10:30:00Z"
        }
        
        :param transport: Transport mode ("dual", "stdio", "http")
        :param port: HTTP port (None for stdio-only)
        :param host: HTTP host
        :param path: HTTP path
        """
        
    @classmethod
    def read_state(cls, base_path: Path) -> Optional[Dict]:
        """
        Read server state (for sub-agents).
        
        :param base_path: Path to .praxis-os directory
        :return: State dict or None if not found/invalid
        """
        
    def cleanup_state(self) -> None:
        """Remove state file on shutdown."""
        
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available by attempting bind."""
```

**Key Features:**
- ✅ Tries preferred port first (4242)
- ✅ Auto-increments if taken (4243, 4244, ...)
- ✅ Writes comprehensive state file
- ✅ Includes PID and timestamp for health checks
- ✅ Cleanup on shutdown

---

### 2. TransportManager (`mcp_server/transport_manager.py`)

**Responsibility:** Handle different transport modes and orchestration

```python
class TransportManager:
    """Manages transport mode execution and lifecycle."""
    
    def __init__(self, mcp_server: FastMCP, config: ServerConfig):
        """Initialize with MCP server and configuration."""
        self.mcp_server = mcp_server
        self.config = config
        self.http_thread: Optional[threading.Thread] = None
        
    def run_dual_mode(self, http_host: str, http_port: int, http_path: str) -> None:
        """
        Run dual transport mode: stdio (main) + HTTP (background).
        
        Flow:
        1. Start HTTP server in daemon thread
        2. Wait for HTTP server to be ready (health check)
        3. Run stdio in main thread (blocks until shutdown)
        4. On shutdown, stop HTTP thread
        
        :param http_host: Host for HTTP server
        :param http_port: Port for HTTP server
        :param http_path: Path for MCP endpoint
        """
        
    def run_stdio_mode(self) -> None:
        """Run stdio-only mode (IDE communication only)."""
        
    def run_http_mode(self, host: str, port: int, path: str) -> None:
        """Run HTTP-only mode (network communication only)."""
        
    def _start_http_thread(
        self, host: str, port: int, path: str
    ) -> threading.Thread:
        """
        Start HTTP server in background daemon thread.
        
        Thread behavior:
        - Daemon thread (dies with main thread)
        - Logs startup/errors separately
        - Graceful shutdown on main thread exit
        
        :return: Running thread
        """
        
    def _wait_for_http_ready(self, host: str, port: int, timeout: int = 5) -> bool:
        """
        Wait for HTTP server to be ready.
        
        Makes test requests until server responds or timeout.
        
        :param host: HTTP host
        :param port: HTTP port  
        :param timeout: Max seconds to wait
        :return: True if ready, False if timeout
        """
        
    def shutdown(self) -> None:
        """Graceful shutdown of all transports."""
```

**Key Features:**
- ✅ Orchestrates stdio + HTTP concurrently
- ✅ Health checks for HTTP readiness
- ✅ Graceful shutdown handling
- ✅ Thread safety for dual mode

---

### 3. Updated Entry Point (`mcp_server/__main__.py`)

**Responsibility:** CLI parsing, initialization, transport mode execution

```python
def main() -> None:
    """
    Entry point with explicit transport mode.
    
    CLI Usage:
        python -m mcp_server --transport dual
        python -m mcp_server --transport stdio
        python -m mcp_server --transport http
    """
    
    # 1. Parse CLI arguments
    parser = argparse.ArgumentParser(
        description="Agent OS MCP Server with dual-transport support"
    )
    parser.add_argument(
        "--transport",
        choices=["dual", "stdio", "http"],
        required=True,
        help=(
            "Transport mode: "
            "dual (stdio for IDE + HTTP for sub-agents), "
            "stdio (IDE only), "
            "http (network only)"
        )
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    args = parser.parse_args()
    
    # 2. Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    
    logger.info("=" * 60)
    logger.info("Agent OS MCP Server")
    logger.info("Transport Mode: %s", args.transport)
    logger.info("=" * 60)
    
    try:
        # 3. Find and validate .praxis-os directory
        base_path = find_agent_os_directory()
        logger.info("Base path: %s", base_path)
        
        # 4. Load and validate configuration
        config = ConfigLoader.load(base_path)
        errors = ConfigValidator.validate(config)
        if errors:
            for error in errors:
                logger.error("Config error: %s", error)
            sys.exit(1)
            
        # 5. Initialize port manager
        port_manager = PortManager(base_path)
        
        # 6. Create MCP server (RAG, workflow, watchers, etc.)
        factory = ServerFactory(config)
        mcp = factory.create_server()
        
        # 7. Initialize transport manager
        transport_mgr = TransportManager(mcp, config)
        
        # 8. Execute based on transport mode
        if args.transport == "dual":
            # Find available port
            http_port = port_manager.find_available_port(config.mcp.http_port)
