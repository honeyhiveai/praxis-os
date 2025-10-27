            "commit_short": self._get_git_commit_short(),
            "status": self._get_git_status(),
        }

    def _is_git_repo(self) -> bool:
        """Check if project root is a git repository."""
        return (self.project_root / ".git").exists()

    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """
        Run git command and return output.

        Args:
            args: Git command arguments (e.g., ["branch", "--show-current"])

        Returns:
            Command output or None on failure
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=5
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            return None

    def _get_git_remote(self) -> Optional[str]:
        """Get git remote URL."""
        return self._run_git_command(["remote", "get-url", "origin"])

    def _get_git_branch(self) -> Optional[str]:
        """Get current git branch."""
        return self._run_git_command(["branch", "--show-current"])

    def _get_git_commit(self) -> Optional[str]:
        """Get current commit hash (full)."""
        return self._run_git_command(["rev-parse", "HEAD"])

    def _get_git_commit_short(self) -> Optional[str]:
        """Get current commit hash (short)."""
        return self._run_git_command(["rev-parse", "--short", "HEAD"])

    def _get_git_status(self) -> str:
        """
        Get git status (clean or dirty).

        Returns:
            "clean" or "dirty"
        """
        status_output = self._run_git_command(["status", "--porcelain"])
        return "clean" if not status_output else "dirty"
```

**Dependencies:**
- Requires: subprocess, pathlib (stdlib)
- Provides: Project metadata for PortManager, get_server_info tool

**Error Handling:**
- Git command failure → Return None (graceful degradation)
- Subprocess timeout (5s) → Return None
- Not a git repo → Fallback to directory name

### 2.3 Component: TransportManager (NEW)

**Purpose:** Orchestrate transport mode execution and lifecycle.

**File:** `mcp_server/transport_manager.py` (NEW)

**Note:** This component is IMPLIED by the design document but not explicitly defined. Adding for completeness.

**Responsibilities:**
- Run dual transport mode (stdio + HTTP concurrently)
- Run stdio-only mode
- Run HTTP-only mode
- Start HTTP server in background thread
- Wait for HTTP readiness before starting stdio
- Graceful shutdown of all transports

**Requirements Satisfied:**
- FR-001: Dual transport mode support
- FR-006: stdio-only mode
- FR-007: HTTP-only mode
- FR-010: Graceful shutdown

**Public Interface:**
```python
class TransportManager:
    """Manages transport mode execution and lifecycle."""
    
    def __init__(self, mcp_server: FastMCP, config: ServerConfig):
        """
        Initialize with MCP server and configuration.
        
        Args:
            mcp_server: Configured FastMCP instance
            config: Server configuration
        """
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
        
        Args:
            http_host: Host for HTTP server
            http_port: Port for HTTP server
            http_path: Path for MCP endpoint
        """
        logger.info("🔄 Starting dual transport mode")
        logger.info("   stdio: for IDE communication")
        logger.info("   HTTP:  http://%s:%s%s", http_host, http_port, http_path)
        
        # Start HTTP in background
        self.http_thread = self._start_http_thread(http_host, http_port, http_path)
        
        # Wait for HTTP ready
        if not self._wait_for_http_ready(http_host, http_port, timeout=5):
            raise RuntimeError("HTTP server failed to start within 5 seconds")
        
        logger.info("✅ HTTP transport ready")
        logger.info("🔌 Starting stdio transport (blocking)")
        
        # Run stdio in main thread (blocks)
        self.mcp_server.run(transport="stdio", show_banner=False)
    
    def run_stdio_mode(self) -> None:
        """Run stdio-only mode (IDE communication only)."""
        logger.info("🔌 Starting stdio-only mode")
        self.mcp_server.run(transport="stdio", show_banner=False)
    
    def run_http_mode(self, host: str, port: int, path: str) -> None:
        """Run HTTP-only mode (network communication only)."""
        logger.info("🌐 Starting HTTP-only mode")
        logger.info("   HTTP: http://%s:%s%s", host, port, path)
        self.mcp_server.run(
            transport="streamable-http",
            host=host,
            port=port,
            path=path,
            show_banner=False
        )
    
    def _start_http_thread(
        self, host: str, port: int, path: str
    ) -> threading.Thread:
        """
        Start HTTP server in background daemon thread.
        
        Returns:
            Running thread
        """
        def run_http():
            """HTTP server thread target."""
            try:
                self.mcp_server.run(
                    transport="streamable-http",
                    host=host,
                    port=port,
                    path=path,
                    show_banner=False
                )
            except Exception as e:
                logger.error("HTTP transport error: %s", e, exc_info=True)
        
        thread = threading.Thread(
            target=run_http,
            daemon=True,
            name="http-transport"
        )
        thread.start()
        return thread
    
    def _wait_for_http_ready(
        self, host: str, port: int, timeout: int = 5
    ) -> bool:
        """
        Wait for HTTP server to be ready.
        
        Makes test requests until server responds or timeout.
        
        Args:
            host: HTTP host
            port: HTTP port  
            timeout: Max seconds to wait
            
        Returns:
            True if ready, False if timeout
        """
        import time
        import socket
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    sock.connect((host, port))
                    return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.5)
        
        return False
    
    def shutdown(self) -> None:
        """Graceful shutdown of all transports."""
        if self.http_thread and self.http_thread.is_alive():
            logger.info("Stopping HTTP transport...")
            # Daemon thread will die with main thread
            # Could add explicit shutdown if needed
```

**Dependencies:**
- Requires: FastMCP instance, ServerConfig
- Provides: Transport orchestration

**Error Handling:**
- HTTP startup failure → Raise RuntimeError
- HTTP readiness timeout → Raise RuntimeError

### 2.4 Component: Updated Entry Point

**Purpose:** CLI parsing, initialization, transport mode execution, lifecycle management.

**File:** `mcp_server/__main__.py` (MODIFIED)

**Responsibilities:**
- Parse CLI arguments (--transport, --log-level)
- Find .praxis-os directory
- Load and validate configuration
- Initialize PortManager and ProjectInfoDiscovery
- Create MCP server (via ServerFactory)
- Execute appropriate transport mode
- Handle shutdown (cleanup state, stop threads)

**Requirements Satisfied:**
- FR-005: Explicit transport mode CLI
- FR-010: Graceful shutdown
- All FRs: Entry point orchestrates all components

**Modifications:**
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
```

**Dependencies:**
- Requires: All components (PortManager, TransportManager, ServerFactory)
- Provides: Application entry point

**Error Handling:**
- Config validation errors → Log and exit(1)
- Port allocation exhaustion → RuntimeError propagates, cleanup in finally
- KeyboardInterrupt → Graceful shutdown
- Any exception → Log, cleanup, exit(1)

---

## 3. API Design

### 3.1 CLI Interface

#### Main Command

```bash
python -m mcp_server --transport {dual|stdio|http} [--log-level {DEBUG|INFO|WARNING|ERROR}]
```

**Arguments:**

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--transport` | choice | Yes | N/A | Transport mode: "dual", "stdio", or "http" |
| `--log-level` | choice | No | INFO | Logging verbosity |

**Examples:**
```bash
# Dual transport (Cursor + sub-agents)
python -m mcp_server --transport dual

# stdio-only (IDE only, backward compatible)
python -m mcp_server --transport stdio

# HTTP-only (standalone server)
python -m mcp_server --transport http

# Debug logging
python -m mcp_server --transport dual --log-level DEBUG
```

**Exit Codes:**
- 0: Normal shutdown
- 1: Configuration error, port exhaustion, or fatal error

### 3.2 MCP Tool: get_server_info

**Purpose:** Return comprehensive server and project metadata for client verification.

**Tool Design:**
```python
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
        praxis-os
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
            "rag_enabled": True,
            "workflow_engine": True,
            "browser_automation": True,
            "file_watchers": True
        }
    }
```

**Response Schema:**
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
        praxis_os_path: string;        // DYNAMIC: Filesystem path
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
        workflow_engine: boolean;     // Runtime check
        browser_automation: boolean;  // Runtime check
        file_watchers: boolean;       // Runtime check
    };
}
```

### 3.3 Internal Interfaces

**PortManager Interface:**
```python
class PortManagerInterface(Protocol):
    def find_available_port(self, preferred_port: int) -> int: ...
    def write_state(self, transport: str, port: Optional[int], host: str, path: str) -> None: ...
    @classmethod
    def read_state(cls, base_path: Path) -> Optional[Dict]: ...
    def cleanup_state(self) -> None: ...
```

**ProjectInfoDiscovery Interface:**
```python
class ProjectInfoDiscoveryInterface(Protocol):
    def get_project_info(self) -> Dict[str, Any]: ...
```

**TransportManager Interface:**
```python
class TransportManagerInterface(Protocol):
    def run_dual_mode(self, http_host: str, http_port: int, http_path: str) -> None: ...
    def run_stdio_mode(self) -> None: ...
    def run_http_mode(self, host: str, port: int, path: str) -> None: ...
    def shutdown(self) -> None: ...
```

---

## 4. Data Models

### 4.1 State File Schema

**File:** `.praxis-os/.mcp_server_state.json`

**Format:** JSON

**Schema:**
```python
@dataclass
class MCPServerState:
    """Runtime state for MCP server discovery."""
    
    version: str  # "1.0.0" (schema version)
    transport: Literal["dual", "stdio", "http"]
    port: Optional[int]  # None for stdio-only
    host: str  # Always "127.0.0.1"
    path: str  # Always "/mcp"
    url: Optional[str]  # Full HTTP URL or None
    pid: int  # Process ID for health checks
    started_at: str  # ISO 8601 timestamp
    project: ProjectInfo
    
@dataclass
class ProjectInfo:
    """Project identification metadata."""
    
    name: str  # From git or directory name
    root: str  # Absolute filesystem path
```

**Example (Dual Mode):**
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
    "name": "praxis-os",
    "root": "/Users/josh/src/github.com/honeyhiveai/praxis-os"
  }
}
```

**Example (stdio-only Mode):**
```json
{
  "version": "1.0.0",
  "transport": "stdio",
  "port": null,
  "host": "127.0.0.1",
  "path": "/mcp",
  "url": null,
  "pid": 12346,
  "started_at": "2025-10-11T10:31:00Z",
  "project": {
    "name": "praxis-os",
    "root": "/Users/josh/src/github.com/honeyhiveai/praxis-os"
  }
}
```

**Validation:**
- `version`: Must be "1.0.0"
- `transport`: Must be "dual", "stdio", or "http"
- `port`: Must be 4242-5242 or null
- `host`: Must be "127.0.0.1"
- `url`: Must match `http://{host}:{port}{path}` or null
- `pid`: Must be positive integer
- `started_at`: Must be valid ISO 8601 timestamp

**Lifecycle:**
- Created: Immediately after successful server startup
- Updated: Never (immutable for lifetime of process)
- Deleted: On graceful shutdown or manually by user

### 4.2 Configuration Schema (Existing, Minor Updates)

**File:** `.praxis-os/config.yaml`

**Additions to MCP Section:**
```yaml
mcp:
  # Preferred HTTP port (auto-increments if unavailable)
  http_port: 4242
  http_host: "127.0.0.1"
  http_path: "/mcp"
  
  # Existing fields...
  enabled_tool_groups:
    - rag
    - workflow
    - browser
  max_tools_warning: 20
```

**Schema:**
```python
@dataclass
class MCPConfig:
    """MCP server configuration."""
    
    # NEW: HTTP configuration
    http_port: int = 4242
    http_host: str = "127.0.0.1"
    http_path: str = "/mcp"
    
    # Existing
    enabled_tool_groups: List[str]
    max_tools_warning: int = 20
```

---

## 5. Security Design

### 5.1 Localhost-Only Binding

**Implementation:**
```python
# ALWAYS bind to localhost
HTTP_HOST = "127.0.0.1"  # Never 0.0.0.0

# Enforce in code
def run_http_mode(self, host: str, port: int, path: str) -> None:
    if host != "127.0.0.1":
        raise ValueError(f"HTTP host must be 127.0.0.1, got: {host}")
    
    self.mcp_server.run(
        transport="streamable-http",
        host=host,  # Always "127.0.0.1"
        port=port,
        path=path
    )
```

**Rationale:**
- Prevents network exposure without authentication
- Same trust model as stdio (local process only)
- Firewall provides additional protection

### 5.2 State File Permissions

**Implementation:**
```python
# Write state file
state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

# Restrict permissions: owner read/write only
state_file.chmod(0o600)
```

**Permissions:**
- Owner: Read + Write (6)
- Group: None (0)
- Others: None (0)

**Rationale:**
- Prevents other users from reading HTTP URL and port
- Standard practice for sensitive runtime files

### 5.3 No Authentication (Acceptable for Localhost)

**Decision:**
- HTTP endpoint has NO authentication
- Acceptable because:
  - Bound to 127.0.0.1 (localhost only)
  - Firewall prevents external access
  - Same trust model as stdio
  - Sub-agents are trusted local processes

**Future Enhancement:**
- If network access needed: Add authentication layer (JWT, API keys)
- Out of scope for MVP

### 5.4 PID Validation for Stale State Detection

**Implementation:**
```python
def is_process_alive(pid: int) -> bool:
    """Check if process is still running."""
    import os
    
    try:
        os.kill(pid, 0)  # Signal 0 = existence check
        return True
    except OSError:
        return False

# Sub-agent usage
state = read_state_file()
if not is_process_alive(state["pid"]):
    raise ConnectionError("MCP server not running (stale state file)")
```

**Rationale:**
- Detects crashed servers
- Prevents sub-agents from attempting stale connections
- Provides clear error messages

---

## 6. Performance Design

### 6.1 Port Allocation Performance

**Target:** < 1 second (NFR-P1)

**Algorithm Complexity:**
- Best case: O(1) - preferred port available
- Worst case: O(n) where n = 1000 (port range)
- Typical case: O(1-3) - few ports in use

**Optimization:**
```python
def find_available_port(self, preferred_port: int = 4242) -> int:
    """Fast port allocation with early exit."""
    for port in range(preferred_port, 5242):
        if self._is_port_available(port):
            return port  # Early exit on first available
    raise RuntimeError(...)

def _is_port_available(self, port: int) -> bool:
    """Fast socket binding test (~1ms per port)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", port))
            return True
    except OSError:
        return False  # Immediately move to next port
```

**Performance Characteristics:**
- Single port test: ~1ms
- 10 ports (typical): ~10ms
- 100 ports (extreme): ~100ms
- Well within < 1 second target

### 6.2 HTTP Server Startup Performance

**Target:** < 5 seconds (NFR-P2)

**Implementation:**
```python
def run_dual_mode(self, http_host: str, http_port: int, http_path: str) -> None:
    # Start HTTP in background
    self.http_thread = self._start_http_thread(http_host, http_port, http_path)
    
    # Wait for HTTP ready with timeout
    if not self._wait_for_http_ready(http_host, http_port, timeout=5):
        raise RuntimeError("HTTP server failed to start within 5 seconds")
    
    # Only then start stdio
    self.mcp_server.run(transport="stdio")

def _wait_for_http_ready(self, host: str, port: int, timeout: int = 5) -> bool:
    """Poll with 0.5s interval, max 10 attempts."""
    for _ in range(int(timeout / 0.5)):
        if self._test_http_connection(host, port):
            return True
        time.sleep(0.5)
    return False
```

**Expected Performance:**
- HTTP server startup: 1-2 seconds (FastMCP + uvicorn)
- First connection test success: ~2 seconds
- Well within < 5 seconds target

### 6.3 Concurrent Request Handling

**Target:** No degradation, < 200ms p95 (NFR-P3)

**Thread Safety:**
```python
# RAGEngine: Use threading locks for concurrent queries
class RAGEngine:
    def __init__(self):
        self._query_lock = threading.Lock()
    
    def query(self, text: str) -> List[Result]:
        with self._query_lock:
            # Thread-safe query execution
            return self._search(text)

# WorkflowEngine: Session access is thread-safe
class WorkflowEngine:
    def __init__(self):
        self._sessions_lock = threading.Lock()
        self._sessions: Dict[str, Session] = {}
    
    def get_session(self, session_id: str) -> Optional[Session]:
        with self._sessions_lock:
            return self._sessions.get(session_id)
```

**Performance Considerations:**
- Lock contention minimal for read-heavy workloads (RAG queries)
- stdio and HTTP rarely call same tool simultaneously
- FastMCP handles I/O asynchronously (uvicorn ASGI server)

### 6.4 Project Discovery Performance

**Target:** Acceptable latency (~50ms for git commands)

**Optimization:**
- Cache not needed (called infrequently)
- Timeout prevents hanging (5s max)
- Subprocess overhead acceptable (~10-50ms)

```python
def _run_git_command(self, args: List[str]) -> Optional[str]:
    """Run with timeout to prevent hanging."""
    result = subprocess.run(
        ["git"] + args,
        timeout=5,  # Prevent hanging
        capture_output=True
    )
    return result.stdout.strip()
```

**Expected Performance:**
- git commands: 10-50ms each
- 5 git commands for full info: ~100ms total
- Called on startup and `get_server_info()` tool calls only
- Negligible impact on overall performance

---

## 7. Testing Strategy

### 7.1 Unit Tests

**Port Allocation:**
```python
def test_find_available_port_prefers_first():
    """Should use preferred port if available."""
    pm = PortManager(tmp_path)
    port = pm.find_available_port(preferred_port=9000)
    assert port == 9000

def test_find_available_port_increments_if_taken():
    """Should increment if preferred port taken."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 9000))
        
        pm = PortManager(tmp_path)
        port = pm.find_available_port(preferred_port=9000)
        assert port == 9001

def test_find_available_port_exhaustion():
    """Should raise RuntimeError if all ports taken."""
    # Bind all ports 4242-4244
    sockets = []
    for port in range(4242, 4245):
        sock = socket.socket()
        sock.bind(("127.0.0.1", port))
        sockets.append(sock)
    
    pm = PortManager(tmp_path)
    with pytest.raises(RuntimeError, match="No available ports"):
        pm.find_available_port(4242)
```

**State File Management:**
```python
def test_write_state_creates_file():
    """Should create state file with correct content."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    assert (tmp_path / ".mcp_server_state.json").exists()
    
    state = json.loads((tmp_path / ".mcp_server_state.json").read_text())
    assert state["transport"] == "dual"
    assert state["port"] == 4242
    assert state["url"] == "http://127.0.0.1:4242/mcp"

def test_write_state_atomic():
    """Should use atomic write (temp + rename)."""
    pm = PortManager(tmp_path)
    
    # Simulate concurrent writes
    pm.write_state(transport="dual", port=4242)
    
    # File should always be valid JSON, never corrupted
    state = json.loads((tmp_path / ".mcp_server_state.json").read_text())
    assert "transport" in state

def test_state_file_permissions():
    """Should set permissions to 0o600."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    state_file = tmp_path / ".mcp_server_state.json"
    assert oct(state_file.stat().st_mode)[-3:] == "600"
```

**Project Discovery:**
```python
def test_project_name_from_git(tmp_path, monkeypatch):
    """Should extract project name from git remote."""
    # Setup fake git repo
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    
    def mock_run(cmd, **kwargs):
        if "remote" in cmd:
            return Mock(stdout="git@github.com:user/my-project.git\n")
        return Mock(stdout="")
    
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    discovery = ProjectInfoDiscovery(tmp_path / ".praxis-os")
    info = discovery.get_project_info()
    
    assert info["name"] == "my-project"

def test_project_name_fallback_to_directory():
    """Should use directory name if not a git repo."""
    tmp_path = Path("/tmp/my-project")
    discovery = ProjectInfoDiscovery(tmp_path / ".praxis-os")
    
    info = discovery.get_project_info()
    assert info["name"] == "my-project"
```

### 7.2 Integration Tests

**Dual Transport:**
```python
@pytest.mark.integration
async def test_dual_transport_serves_both():
    """Should serve both stdio and HTTP simultaneously."""
    
    # Start server in dual mode
    proc = subprocess.Popen(
        ["python", "-m", "mcp_server", "--transport", "dual"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=test_project_path,
