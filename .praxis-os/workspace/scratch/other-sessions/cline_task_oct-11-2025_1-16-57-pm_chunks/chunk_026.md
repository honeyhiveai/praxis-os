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
        base_path = find_praxis_os_directory()
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


def find_praxis_os_directory() -> Path:
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

## Error Handling

### Port Allocation Failures

```python
try:
    port = port_manager.find_available_port(4242)
except RuntimeError as e:
    logger.error(
        "No available ports in range 4242-5242. "
        "This suggests %d MCP servers already running!",
        5242 - 4242
    )
    sys.exit(1)
```

**User Action:** Close some Cursor windows to free ports

---

### State File Corruption

```python
try:
    state = json.loads(state_file.read_text())
except json.JSONDecodeError:
    logger.error("State file corrupted: %s", state_file)
    # Delete and regenerate
    state_file.unlink()
    return None
```

**User Action:** Restart MCP server to regenerate state file

---

### HTTP Server Startup Failure

```python
try:
    mcp.run(transport="streamable-http", host=host, port=port, path=path)
except Exception as e:
    logger.error("HTTP server failed to start: %s", e)
    # Cleanup state file (don't advertise unavailable server)
    port_manager.cleanup_state()
    raise
```

**User Action:** Check logs, possibly firewall/permissions issue

---

### Stale State File (Server Crashed)

```python
# Sub-agent checks PID validity
state = read_state_file()
if not is_process_alive(state["pid"]):
    logger.warning(
        "MCP server (PID %d) is not running. "
        "State file is stale. Please restart Cursor.",
        state["pid"]
    )
    return None
```

**User Action:** Restart IDE/MCP server

---

## Security Considerations

### Localhost-Only Binding

```python
# Always bind to localhost
HTTP_HOST = "127.0.0.1"  # Never 0.0.0.0

# State file explicitly documents this
{
  "host": "127.0.0.1",  # Not exposed to network
  "url": "http://127.0.0.1:4243/mcp"
}
```

**Rationale:** MCP server contains project-specific code and data. Should never be exposed to network.

---

### No Authentication (Acceptable for Localhost)

- HTTP endpoint has NO authentication
- Acceptable because:
  - Bound to 127.0.0.1 (localhost only)
  - Firewall prevents external access
  - Same trust model as stdio

**If network access needed:** Add authentication layer (out of scope)

---

### State File Permissions

```python
# Write state file with restricted permissions
state_file.write_text(json.dumps(state), encoding="utf-8")
state_file.chmod(0o600)  # Owner read/write only
```

**Rationale:** State file contains port/URL info. Prevent other users from accessing.

---

## Testing Strategy

### Unit Tests

```python
# tests/test_port_manager.py

def test_port_allocation_prefers_first():
    """Port manager should use preferred port if available."""
    pm = PortManager(tmp_path)
    port = pm.find_available_port(preferred_port=9000)
    assert port == 9000

def test_port_allocation_increments_if_taken():
    """Port manager should increment if preferred port taken."""
    # Bind to 9000
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 9000))
        
        # Should get 9001
        pm = PortManager(tmp_path)
        port = pm.find_available_port(preferred_port=9000)
        assert port == 9001

def test_state_file_written_correctly():
    """State file should contain all required fields."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    state = pm.read_state(tmp_path)
    assert state["transport"] == "dual"
    assert state["port"] == 4242
    assert state["url"] == "http://127.0.0.1:4242/mcp"
    assert "pid" in state
    assert "started_at" in state
```

---

### Integration Tests

```python
# tests/test_dual_transport.py

@pytest.mark.integration
async def test_dual_transport_serves_both():
    """Dual transport should serve both stdio and HTTP."""
    
    # Start server in dual mode
    proc = subprocess.Popen(
        ["python", "-m", "mcp_server", "--transport", "dual"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=test_project_path,
    )
    
    # Wait for state file
    state = wait_for_state_file(test_project_path / ".praxis-os")
    
    # Test HTTP endpoint
    response = requests.post(
        state["url"],
        json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
        headers={"Accept": "application/json, text/event-stream"}
    )
    assert response.status_code == 200
    
    # Test stdio
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"tools/list","id":1}\n')
    proc.stdin.flush()
    line = proc.stdout.readline()
    result = json.loads(line)
    assert "result" in result
    
    # Cleanup
    proc.terminate()
```

---

### Multi-Project Tests

```python
# tests/test_multi_project.py

@pytest.mark.integration
def test_multiple_projects_no_conflicts():
    """Multiple projects should get different ports."""
    
    # Start 3 servers
    servers = []
    for project in [project_a, project_b, project_c]:
        proc = start_server(project, transport="http")
        servers.append(proc)
    
    # Read state files
    state_a = read_state(project_a / ".praxis-os")
    state_b = read_state(project_b / ".praxis-os")
    state_c = read_state(project_c / ".praxis-os")
    
    # All should have different ports
    assert state_a["port"] != state_b["port"]
    assert state_b["port"] != state_c["port"]
    assert state_a["port"] != state_c["port"]
    
    # All should be accessible
    assert is_server_responding(state_a["url"])
    assert is_server_responding(state_b["url"])
    assert is_server_responding(state_c["url"])
    
    # Cleanup
    for proc in servers:
        proc.terminate()
```

---

## Migration Path

### Phase 1: Implementation (Week 1)

**Tasks:**
1. ✅ Create `port_manager.py` module
2. ✅ Create `transport_manager.py` module
3. ✅ Update `__main__.py` with CLI args
4. ✅ Update `.cursor/mcp.json` with `--transport dual`
5. ✅ Add `.mcp_server_state.json` to `.gitignore`
6. ✅ Unit tests for port allocation
7. ✅ Unit tests for state file management

---

### Phase 2: Testing (Week 1-2)

**Tasks:**
1. ✅ Integration tests for dual transport
2. ✅ Multi-project conflict tests
3. ✅ Manual testing with Cursor
4. ✅ Manual testing with multiple windows
5. ✅ Load testing (10+ projects)
6. ✅ Error scenario testing (port exhaustion, etc.)

---

### Phase 3: Sub-Agent Integration (Week 2)

**Tasks:**
1. ✅ Create discovery utility (`mcp_client_example.py`)
2. ✅ Document sub-agent integration pattern
3. ✅ Test with Cline (if available)
4. ✅ Test with Aider (if available)
5. ✅ Create example custom sub-agent

---

### Phase 4: Documentation (Week 2-3)

**Tasks:**
1. ✅ Update README with dual-transport setup
2. ✅ Create sub-agent integration guide
3. ✅ Add troubleshooting section
4. ✅ Create architecture diagrams
5. ✅ Video walkthrough (optional)

---

### Phase 5: Rollout (Week 3)

**Tasks:**
1. ✅ Merge to main branch
2. ✅ Update installation instructions
3. ✅ Announce in docs/changelog
4. ✅ Monitor for issues
5. ✅ Provide user support

---

## Future Enhancements

### 1. Health Check Endpoint

```python
@mcp.tool()
def health_check() -> dict:
    """
    Health check endpoint for monitoring.
    
    Returns:
        {
          "status": "healthy",
          "uptime_seconds": 3600,
          "transport": "dual",
          "tools_available": 15,
          "rag_index_size": 1234
        }
    """
```

**Use Case:** Sub-agents verify server before connecting

---

### 2. Automatic Reconnection

```python
class SubAgentClient:
    """Client with automatic reconnection."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.url = None
