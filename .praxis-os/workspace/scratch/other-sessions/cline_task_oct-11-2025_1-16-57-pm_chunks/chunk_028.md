            http_host = config.mcp.http_host
            http_path = config.mcp.http_path
            
            logger.info("🔄 Starting DUAL transport mode")
            logger.info("   stdio: for IDE communication")
            logger.info("   HTTP:  http://%s:%s%s", http_host, http_port, http_path)
            
            # Write state file
            port_manager.write_state(
                transport="dual",
                port=http_port,
                host=http_host,
                path=http_path
            )
            
            # Run dual mode (blocks)
            transport_mgr.run_dual_mode(http_host, http_port, http_path)
            
        elif args.transport == "stdio":
            logger.info("🔌 Starting stdio-only mode")
            
            # Write state file (no HTTP port)
            port_manager.write_state(transport="stdio", port=None)
            
            # Run stdio mode (blocks)
            transport_mgr.run_stdio_mode()
            
        elif args.transport == "http":
            # Find available port
            http_port = port_manager.find_available_port(config.mcp.http_port)
            http_host = config.mcp.http_host
            http_path = config.mcp.http_path
            
            logger.info("🌐 Starting HTTP-only mode")
            logger.info("   HTTP: http://%s:%s%s", http_host, http_port, http_path)
            
            # Write state file
            port_manager.write_state(
                transport="http",
                port=http_port,
                host=http_host,
                path=http_path
            )
            
            # Run HTTP mode (blocks)
            transport_mgr.run_http_mode(http_host, http_port, http_path)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C)")
    except Exception as e:
        logger.error("Fatal error: %s", e, exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if 'port_manager' in locals():
            port_manager.cleanup_state()
        if 'transport_mgr' in locals():
            transport_mgr.shutdown()
            
        logger.info("Shutdown complete")


def find_agent_os_directory() -> Path:
    """
    Find .praxis-os directory.
    
    Search order:
    1. Current directory: ./.praxis-os
    2. Parent directory: ../.praxis-os (when run as module)
    3. Home directory: ~/.praxis-os
    
    :return: Path to .praxis-os directory
    :raises SystemExit: If not found
    """
```

**Key Features:**
- ✅ Explicit transport mode (required argument)
- ✅ Clear logging of startup parameters
- ✅ Graceful shutdown handling
- ✅ State file cleanup
- ✅ Multiple .praxis-os search paths

---

## Project Information Discovery

### Overview

HTTP clients need to verify they're connected to the correct MCP server (right project, right port). This is especially critical when:
- Multiple projects are open (different ports)
- Remote agents connect to multiple servers
- Debugging connection issues
- Displaying project context in agent UI

**Solution:** Dynamic project information discovery with verification tools

---

### Component: ProjectInfoDiscovery

**Responsibility:** Dynamically discover project metadata at runtime (NO hardcoded values)

**Location:** `mcp_server/project_info.py`

```python
class ProjectInfoDiscovery:
    """
    Discovers project information dynamically.
    
    All information is discovered at runtime via:
    - Git commands (subprocess)
    - Filesystem operations
    - NO hardcoded values
    """

    def __init__(self, base_path: Path):
        """
        Initialize project info discovery.

        :param base_path: Path to .praxis-os directory
        """
        self.base_path = base_path
        self.project_root = base_path.parent  # Discovered from filesystem

    def get_project_info(self) -> Dict:
        """
        Get comprehensive project information (DYNAMIC).

        Discovers:
        - Project name (from git or directory)
        - Project root path (from filesystem)
        - Git repository info (if available)
        - Agent OS path

        ALL values are discovered at runtime.

        :return: Project information dict
        """
        return {
            "name": self._get_project_name(),        # Git repo OR dir name
            "root": str(self.project_root),          # Filesystem path
            "agent_os_path": str(self.base_path),    # Filesystem path
            "git": self._get_git_info(),             # Git commands OR None
        }

    def _get_project_name(self) -> str:
        """
        Get project name dynamically.

        Priority:
        1. Git repository name (from remote URL)
        2. Directory name (fallback)

        Examples:
        - git@github.com:user/agent-os-enhanced.git → "agent-os-enhanced"
        - /Users/josh/my-project/ → "my-project"

        :return: Project name (NEVER hardcoded)
        """
        # Try git repository name first
        git_name = self._get_git_repo_name()
        if git_name:
            return git_name

        # Fallback to directory name
        return self.project_root.name

    def _get_git_info(self) -> Optional[Dict]:
        """
        Get git repository information dynamically.

        Runs git commands:
        - git remote get-url origin
        - git branch --show-current
        - git rev-parse HEAD
        - git status --porcelain

        :return: Git info dict or None if not a git repo
        """
        if not self._is_git_repo():
            return None

        return {
            "remote": self._get_git_remote(),          # subprocess call
            "branch": self._get_git_branch(),          # subprocess call
            "commit": self._get_git_commit(),          # subprocess call
            "commit_short": self._get_git_commit_short(),  # subprocess call
            "status": self._get_git_status(),          # subprocess call
        }
```

**Key Features:**
- ✅ No hardcoded project names
- ✅ No hardcoded paths (derived from base_path)
- ✅ Subprocess calls for git info
- ✅ Graceful fallback if not a git repo
- ✅ Fresh data on every call

---

### Integration: State File

**State file includes basic project info for fast discovery:**

```json
{
  "version": "1.0.0",
  "transport": "dual",
  "port": 4243,
  "host": "127.0.0.1",
  "path": "/mcp",
  "url": "http://127.0.0.1:4243/mcp",
  "pid": 12345,
  "started_at": "2025-10-11T10:30:00Z",
  
  "project": {
    "name": "agent-os-enhanced",
    "root": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced"
  }
}
```

**Generated dynamically in `PortManager.write_state()`:**

```python
class PortManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.project_discovery = ProjectInfoDiscovery(base_path)
    
    def write_state(self, transport: str, port: Optional[int], ...):
        """Write state file with dynamically discovered project info."""
        
        # DYNAMIC discovery - happens at runtime
        project_info = self.project_discovery.get_project_info()
        
        state = {
            "version": "1.0.0",
            "transport": transport,
            "port": port,
            # ... other fields ...
            
            # DYNAMIC - NO hardcoded values
            "project": {
                "name": project_info["name"],      # From git or directory
                "root": project_info["root"]       # From filesystem
            }
        }
        
        self.state_file.write_text(json.dumps(state, indent=2))
```

---

### Integration: MCP Tool

**New Tool: `get_server_info`**

**Purpose:** Return comprehensive server and project metadata for client verification

**Tool Design (follows MCP best practices):**
- ✅ Verb-noun naming pattern
- ✅ Single responsibility (return server info)
- ✅ Granular (not parameterized)
- ✅ Complete docstring with example
- ✅ Type hints

```python
# In mcp_server/server/tools/server_info_tools.py

def register_server_info_tools(
    mcp: FastMCP,
    project_discovery: ProjectInfoDiscovery,
    start_time: float,
    start_timestamp: str,
    get_transport_mode_fn: Callable,
) -> None:
    """
    Register server information tools.
    
    :param mcp: FastMCP server instance
    :param project_discovery: Project info discovery service
    :param start_time: Server start time (for uptime)
    :param start_timestamp: ISO 8601 start timestamp
    :param get_transport_mode_fn: Function returning current transport mode
    """
    
    @mcp.tool()
    def get_server_info() -> dict:
        """
        Get MCP server and project information for client verification.
        
        Returns comprehensive metadata including:
        - Server transport mode and uptime
        - Project identification (name, root, git info)
        - Available capabilities (RAG, workflows, browser)
        
        This tool enables HTTP clients to:
        - Verify connection to correct project
        - Display project context in UI
        - Validate server capabilities before use
        - Debug connection issues
        
        Returns:
            dict: Server and project metadata
            
        Example:
            >>> info = get_server_info()
            >>> print(f"Connected to: {info['project']['name']}")
            agent-os-enhanced
            >>> print(f"Git branch: {info['project']['git']['branch']}")
            main
            >>> print(f"Tools: {info['capabilities']['tools_available']}")
            15
        """
        import os
        import time
        
        # DYNAMIC discovery - called every invocation
        project_info = project_discovery.get_project_info()
        
        return {
            "server": {
                "version": "1.0.0",
                "transport": get_transport_mode_fn(),  # Runtime state
                "uptime_seconds": time.time() - start_time,  # Runtime
                "pid": os.getpid(),  # Runtime
                "started_at": start_timestamp  # Runtime
            },
            "project": project_info,  # DYNAMIC discovery result
            "capabilities": {
                "tools_available": len(mcp.list_tools()),  # Runtime count
                # Additional capabilities discovered at runtime
                "rag_enabled": True,  # From component availability
                "workflow_engine": True,
                "browser_automation": True,
                "file_watchers": True
            }
        }
```

**Return Schema:**

```typescript
interface ServerInfo {
    server: {
        version: string;              // "1.0.0"
        transport: "dual" | "stdio" | "http";
        uptime_seconds: number;       // Runtime calculated
        pid: number;                  // Process ID
        started_at: string;           // ISO 8601 timestamp
    };
    project: {
        name: string;                 // DYNAMIC: From git or directory
        root: string;                 // DYNAMIC: Filesystem path
        agent_os_path: string;        // DYNAMIC: Filesystem path
        git: {                        // DYNAMIC: Git commands, null if not repo
            remote: string;           // "git@github.com:user/repo.git"
            branch: string;           // "main"
            commit: string;           // Full SHA
            commit_short: string;     // Short SHA
            status: "clean" | "dirty";
        } | null;
    };
    capabilities: {
        tools_available: number;      // Runtime count
        rag_enabled: boolean;         // Runtime check
        rag_index_chunks: number;     // From RAG engine
        workflow_engine: boolean;     // Runtime check
        browser_automation: boolean;  // Runtime check
        file_watchers: boolean;       // Runtime check
    };
}
```

---

### Integration: ServerFactory

**Wire project discovery through dependency injection:**

```python
class ServerFactory:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.paths = config.resolved_paths
        
        # Initialize project discovery at startup
        self.project_discovery = ProjectInfoDiscovery(config.base_path)
        
        # Track startup for uptime calculation
        self.start_time = time.time()
        self.start_timestamp = datetime.now(timezone.utc).isoformat()
    
    def create_server(self) -> FastMCP:
        """Create fully configured MCP server."""
        
        # ... create components ...
        
        # Pass project_discovery to tool registration
        tool_count = register_all_tools(
            mcp=mcp,
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            project_discovery=self.project_discovery,  # ← Inject
            start_time=self.start_time,
            start_timestamp=self.start_timestamp,
            # ... other dependencies
        )
        
        return mcp
```

---

### Client Verification Flow

**Two-stage verification:**

```python
# Stage 1: Fast discovery via state file
state = read_state_file(".praxis-os/.mcp_server_state.json")
print(f"Found server for project: {state['project']['name']}")

# Verify basic info
if state['project']['root'] != expected_project_root:
    raise ValueError(f"Wrong project in state file!")

# Stage 2: Thorough verification via MCP tool
client = connect_to_mcp(state['url'])
info = client.call_tool("get_server_info", {})

# Verify detailed project info
if info['project']['root'] != expected_project_root:
    raise ValueError(f"Wrong project! Expected {expected_project_root}")

# Verify git branch (if relevant)
if info['project']['git']:
    if info['project']['git']['branch'] != expected_branch:
        print(f"⚠️  Warning: On branch {info['project']['git']['branch']}, "
              f"expected {expected_branch}")

# Verify capabilities
if not info['capabilities']['rag_enabled']:
    raise ValueError("RAG not available on this server")

# Success!
print(f"✅ Verified connection to {info['project']['name']}")
print(f"   Root: {info['project']['root']}")
print(f"   Branch: {info['project']['git']['branch']}")
print(f"   Commit: {info['project']['git']['commit_short']}")
print(f"   Status: {info['project']['git']['status']}")
print(f"   Tools: {info['capabilities']['tools_available']}")
```

---

### Multi-Project Agent Example

**Agent managing multiple projects simultaneously:**

```python
class MultiProjectAgent:
    """Agent connected to multiple MCP servers."""
    
    def __init__(self):
        self.connections = {}  # project_name -> connection_info
        
    def connect_to_project(self, project_root: Path):
        """Connect and verify project."""
        
        # Discover via state file
        state_file = project_root / ".praxis-os" / ".mcp_server_state.json"
        state = json.loads(state_file.read_text())
        
        # Connect to MCP server
        client = MCPClient(state['url'])
        
        # Get detailed info
        info = client.call_tool("get_server_info", {})
        
        # Store connection
        project_name = info['project']['name']
        self.connections[project_name] = {
            "client": client,
            "info": info,
            "url": state['url']
        }
        
        print(f"✅ Connected to {project_name}")
        print(f"   URL: {state['url']}")
        print(f"   Branch: {info['project']['git']['branch']}")
        print(f"   Tools: {info['capabilities']['tools_available']}")
    
    def list_projects(self):
        """List all connected projects."""
        print("Connected Projects:")
        for name, conn in self.connections.items():
            info = conn['info']
            git = info['project']['git']
            print(f"  • {name}")
            print(f"    └─ {conn['url']}")
            print(f"    └─ {git['branch']} ({git['commit_short']})")
    
    def search_across_all(self, query: str):
        """Search standards across all connected projects."""
        results = {}
        for project_name, conn in self.connections.items():
            print(f"Searching {project_name}...")
            result = conn['client'].call_tool("search_standards", {
                "query": query,
                "n_results": 5
            })
            results[project_name] = result
        return results
```

---

### Dynamic Discovery Flow

```
Server Startup:
  ├─ ServerFactory.__init__(config)
  │   ├─ ProjectInfoDiscovery(base_path)
  │   │   └─ project_root = base_path.parent  (filesystem)
  │   ├─ start_time = time.time()
  │   └─ start_timestamp = datetime.now().isoformat()
  │
  ├─ PortManager.write_state()
  │   ├─ project_discovery.get_project_info()  ← DYNAMIC CALL
  │   │   ├─ _get_project_name()
  │   │   │   ├─ subprocess.run(["git", "remote", "get-url", "origin"])
  │   │   │   │   Success → extract repo name
  │   │   │   │   Failure → use directory name
  │   │   │   └─ Returns: "agent-os-enhanced" (NOT hardcoded!)
  │   │   ├─ _get_git_info()
  │   │   │   ├─ subprocess.run(["git", "branch", "--show-current"])
  │   │   │   ├─ subprocess.run(["git", "rev-parse", "HEAD"])
  │   │   │   └─ subprocess.run(["git", "status", "--porcelain"])
  │   │   └─ Returns: {name, root, agent_os_path, git}
  │   └─ Write to .mcp_server_state.json
  │
  └─ register_all_tools(project_discovery=...)
      └─ @mcp.tool() get_server_info registered

Client Calls Tool:
  └─ get_server_info()
      ├─ project_discovery.get_project_info()  ← FRESH DYNAMIC CALL
      │   └─ Runs git commands AGAIN (fresh data)
      ├─ Collect runtime info (uptime, PID, tool count)
      └─ Return complete server info
```

---

### Benefits

✅ **Client Verification** - Confirm connection to correct project  
✅ **No Hardcoding** - All values discovered at runtime  
✅ **Multi-Project UI** - Display project names, branches, commits  
✅ **Fresh Data** - Tool calls discovery each time (no stale cache)  
✅ **Graceful Fallback** - Works even if not a git repo  
✅ **Git Awareness** - Know exact branch/commit being worked on  
✅ **Debugging Aid** - Clear project identification in logs  
✅ **Remote Agents** - Can validate connection before use  

---

## Configuration

### IDE Configuration (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "comment": "Agent OS RAG/Workflow server with dual transport",
      
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
      
      "transport": "stdio",
      
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "get_workflow_state"
      ]
    }
  }
}
```

**Key Points:**
- `"transport": "stdio"` - IDE's transport to server
- `"--transport", "dual"` - Server's transport modes
- Environment variables for Python path resolution

### Server Configuration (`.praxis-os/config.yaml`)

```yaml
# MCP Server Configuration
mcp:
  # Preferred HTTP port (auto-increments if unavailable)
  http_port: 4242
  http_host: "127.0.0.1"
  http_path: "/mcp"
  
  # Tool groups to enable
  enabled_tool_groups:
    - rag
    - workflow
    - browser
  
  # Warning threshold for tool count
  max_tools_warning: 20

# RAG Configuration
rag:
  standards_path: ".praxis-os/standards"
  usage_path: ".praxis-os/usage"
  workflows_path: ".praxis-os/workflows"
  index_path: ".praxis-os/.cache/vector_index"
  embedding_provider: "local"  # or "openai"
```

---

## Port Management

### Port Allocation Algorithm

```python
def find_available_port(preferred_port: int = 4242) -> int:
    """
    Dynamic port allocation algorithm.
    
    Algorithm:
    1. Try preferred_port (e.g., 4242)
       ├─ Create socket
       ├─ Try bind to 127.0.0.1:4242
       └─ If success → return 4242
    
    2. If port in use:
       ├─ Increment port (4243)
       ├─ Try bind
       └─ Repeat until success or max (5242)
    
    3. If all ports exhausted:
       └─ Raise RuntimeError
    """
    
    for port in range(preferred_port, 5242):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue  # Port in use, try next
    
    raise RuntimeError("No available ports in range 4242-5242")
```

### Port Conflict Resolution

```
Scenario: 3 Cursor windows open same project

Window 1 launches first:
  ├─ Tries port 4242 → ✅ Available
  ├─ Binds to 4242
  └─ Writes state: {"port": 4242}

Window 2 launches:
  ├─ Tries port 4242 → ❌ In use (Window 1 has it)
  ├─ Tries port 4243 → ✅ Available
  ├─ Binds to 4243
  └─ Writes state: {"port": 4243}

Window 3 launches:
  ├─ Tries port 4242 → ❌ In use
  ├─ Tries port 4243 → ❌ In use
  ├─ Tries port 4244 → ✅ Available
  ├─ Binds to 4244
  └─ Writes state: {"port": 4244}

Each window has independent server on different port!
```

### Port Reuse After Shutdown

```
Window 1 shuts down:
  └─ Port 4242 released

Window 4 launches:
  ├─ Tries port 4242 → ✅ Available again
  ├─ Binds to 4242
  └─ Writes state: {"port": 4242}

Ports are reused as they become available!
```

---

## State Management

### State File Format

**Location:** `.praxis-os/.mcp_server_state.json`

```json
{
  "transport": "dual",
  "port": 4243,
  "host": "127.0.0.1",
  "path": "/mcp",
  "url": "http://127.0.0.1:4243/mcp",
  "pid": 12345,
  "started_at": "2025-10-11T10:30:00Z",
  "version": "1.0.0"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `transport` | string | Transport mode: "dual", "stdio", "http" |
| `port` | int or null | HTTP port (null for stdio-only) |
| `host` | string | HTTP host (always "127.0.0.1") |
| `path` | string | HTTP path (always "/mcp") |
| `url` | string or null | Full HTTP URL (null for stdio-only) |
| `pid` | int | Process ID (for health checks) |
| `started_at` | ISO8601 | Server start timestamp |
| `version` | string | State file schema version |

### State File Lifecycle

```
Server Startup:
  ├─ Port allocated (4243)
  ├─ Write .mcp_server_state.json
  └─ Atomic write (temp file + rename)

Server Running:
  └─ State file exists (sub-agents can read)

Server Shutdown:
  ├─ Delete .mcp_server_state.json
  └─ Clean exit

Crash/Kill:
  └─ State file remains (stale)
      ├─ Sub-agents should check PID validity
      └─ Health check before connecting
```

### Gitignore Entry

```bash
# .gitignore
.praxis-os/.mcp_server_state.json
.praxis-os/.cache/
```

**Rationale:** State file is runtime-only, project-specific, not source code

---

## Transport Modes

### Mode 1: Dual (stdio + HTTP)

**Use Case:** Primary IDE with sub-agents

```
Configuration:
  python -m mcp_server --transport dual

Behavior:
  ├─ Main thread: stdio (blocks, serves IDE)
  ├─ Background thread: HTTP on auto-allocated port
  └─ State file: includes HTTP URL

Example:
  Cursor (stdio) + Cline (HTTP) both access same server
```

**Pros:**
- ✅ Single server serves multiple agents
- ✅ IDE controls lifecycle (starts/stops server)
- ✅ Sub-agents auto-discover via state file
- ✅ All agents share same RAG/state/watchers

**Cons:**
- ⚠️ More complex (two transports)
- ⚠️ Requires thread-safe tool implementations

---

### Mode 2: stdio-only

**Use Case:** IDE integration without sub-agents

```
Configuration:
  python -m mcp_server --transport stdio

Behavior:
  ├─ Main thread: stdio only
  ├─ No HTTP server
  └─ State file: no HTTP URL

Example:
  Claude Desktop with no sub-agents
```

**Pros:**
- ✅ Simple, single transport
- ✅ Lower resource usage
- ✅ No port allocation needed

**Cons:**
- ❌ Sub-agents can't connect
- ❌ Only IDE has access

---

### Mode 3: HTTP-only

**Use Case:** Standalone server, all agents via HTTP

```
Configuration:
  python -m mcp_server --transport http

Behavior:
  ├─ Main thread: HTTP on auto-allocated port
  ├─ No stdio
  └─ State file: includes HTTP URL

Example:
  Systemd service, all agents (including IDE) connect via HTTP
```

**Pros:**
- ✅ Multiple agents can connect
- ✅ IDE doesn't control lifecycle
- ✅ Can run as system service

**Cons:**
- ⚠️ IDE must support HTTP transport
- ⚠️ Manual lifecycle management

---

## Multi-Project Support

### Scenario: Multiple Projects Open

```
~/projects/
├─ project-a/
│  ├─ .praxis-os/
│  │  ├─ venv/
│  │  ├─ standards/
│  │  └─ .mcp_server_state.json  → {"port": 4242}
│  └─ .cursor/mcp.json
│
├─ project-b/
│  ├─ .praxis-os/
│  │  ├─ venv/
│  │  ├─ standards/
│  │  └─ .mcp_server_state.json  → {"port": 4243}
│  └─ .cursor/mcp.json
│
└─ project-c/
   ├─ .praxis-os/
   │  ├─ venv/
   │  ├─ standards/
   │  └─ .mcp_server_state.json  → {"port": 4244}
   └─ .cursor/mcp.json

Each project:
  ✅ Independent MCP server
  ✅ Separate port (no conflicts)
  ✅ Project-specific RAG index
  ✅ Watches own .praxis-os/standards/
  ✅ Sub-agents read their project's state file
```

### Project Isolation

| Resource | Shared? | Notes |
|----------|---------|-------|
| MCP Server Process | ❌ No | One per project |
| HTTP Port | ❌ No | Auto-allocated per project |
| RAG Index | ❌ No | `.praxis-os/.cache/vector_index/` |
| File Watchers | ❌ No | Watches project's `.praxis-os/` |
| Workflow State | ❌ No | `.praxis-os/.cache/state/` |
| State File | ❌ No | `.praxis-os/.mcp_server_state.json` |

**Complete isolation ensures no cross-contamination!**

---

## Sub-Agent Integration

### Discovery Pattern

```python
# Sub-agent code (Cline, Aider, custom agent)

from pathlib import Path
import json

def discover_mcp_server(project_root: Path) -> Optional[str]:
    """
    Discover MCP server for this project.
    
    :param project_root: Path to project root
    :return: HTTP URL or None if not found
    """
    state_file = project_root / ".praxis-os" / ".mcp_server_state.json"
    
    if not state_file.exists():
        print("❌ MCP server not running (no state file)")
        return None
    
    try:
        state = json.loads(state_file.read_text())
        
        # Validate server is still running
        if not is_process_alive(state["pid"]):
            print("❌ MCP server crashed (stale state file)")
            return None
        
        # Check if HTTP is available
        if state["url"] is None:
            print("❌ MCP server is stdio-only (no HTTP)")
            return None
        
        print(f"✅ MCP server found: {state['url']}")
        return state["url"]
        
    except Exception as e:
        print(f"❌ Failed to read state file: {e}")
        return None


def is_process_alive(pid: int) -> bool:
    """Check if process is still running."""
    try:
        os.kill(pid, 0)  # Signal 0 = existence check
        return True
    except OSError:
        return False
```

### Cline Integration Example

```json
// Cline's MCP configuration (auto-generated)
{
  "mcpServers": {
    "agent-os-rag": {
      "transport": "streamable-http",
      "url": "http://127.0.0.1:4243/mcp"
    }
  }
}
```

Cline workflow:
1. User opens project in Cline
2. Cline runs discovery script
3. Reads `.praxis-os/.mcp_server_state.json`
4. Extracts URL
5. Connects via HTTP
6. Accesses all MCP tools

---

