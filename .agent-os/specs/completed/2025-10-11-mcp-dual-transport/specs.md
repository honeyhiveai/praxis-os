# Technical Specifications

**Project:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  IDE (Cursor, Windsurf, Claude Desktop)                         │
│  Config: --transport dual                                        │
│  Transport: stdio (stdin/stdout pipes)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ Launches process
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server Process (.agent-os/venv/bin/python)                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Startup Sequence                                          │  │
│  │  1. Parse CLI: --transport dual                          │  │
│  │  2. Load config.yaml                                     │  │
│  │  3. Find available port (4242 → 4243 → ...)            │  │
│  │  4. Initialize components (RAG, Workflow, Watchers)     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Transport Layer (Dual Mode)                              │  │
│  │                                                           │  │
│  │  ┌─────────────────────────┐  ┌──────────────────────┐  │  │
│  │  │ Main Thread             │  │ Background Thread    │  │  │
│  │  │ stdio Transport         │  │ HTTP Transport       │  │  │
│  │  │ Serves: Cursor          │  │ Serves: Sub-agents   │  │  │
│  │  └─────────────────────────┘  └──────────────────────┘  │  │
│  │              ↓                           ↓               │  │
│  │         ┌────────────────────────────────────┐          │  │
│  │         │  FastMCP Server Instance           │          │  │
│  │         │  - Tool Registry                   │          │  │
│  │         │  - RAGEngine                       │          │  │
│  │         │  - WorkflowEngine                  │          │  │
│  │         │  - File Watchers                   │          │  │
│  │         └────────────────────────────────────┘          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ State File: .agent-os/.mcp_server_state.json            │  │
│  │   {transport, port, url, pid, project}                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP: http://127.0.0.1:4243/mcp
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Sub-Agents (Cline, Aider, Custom)                              │
│  1. Read .agent-os/.mcp_server_state.json                      │
│  2. Extract HTTP URL                                            │
│  3. Connect via streamable-http protocol                        │
│  4. Call MCP tools (same tools as IDE)                         │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components:**
- **PortManager:** Dynamic port allocation and state file management
- **ProjectInfoDiscovery:** Runtime project metadata discovery
- **TransportManager:** Orchestrates stdio and HTTP transports concurrently
- **Entry Point:** CLI parsing, initialization, lifecycle management
- **State File:** JSON document for sub-agent discovery

**Architectural Principles:**
- **Single FastMCP Instance:** Both transports share same server for consistency
- **Explicit Configuration:** User specifies transport mode via required CLI flag
- **Automatic Conflict Resolution:** Port allocation eliminates manual configuration
- **Project Isolation:** Each project has independent server, port, state, RAG index
- **Thread-based Concurrency:** Main thread for stdio, daemon thread for HTTP

### 1.2 Architectural Decisions

#### Decision 1: Dual Transport from Single FastMCP Instance

**Decision:** Run both stdio and HTTP transports from a single FastMCP server instance using Python threading.

**Rationale:**
- Satisfies FR-001 (dual transport support)
- Ensures both transports access identical tool registry, RAG index, workflow state
- Validated with working proof-of-concept code using FastMCP and MCP SDK
- Simpler than maintaining two separate server instances

**Alternatives Considered:**
- **Two FastMCP Instances:** More complex state synchronization, double resource usage
- **HTTP-to-stdio Proxy:** Additional layer, increased latency, more failure modes
- **HTTP-only for All:** Requires IDE support for HTTP, breaking change for users

**Trade-offs:**
- **Pros:** Single source of truth, simple architecture, proven feasible
- **Cons:** Requires thread-safe component implementations

#### Decision 2: Automatic Port Allocation (4242-5242)

**Decision:** Automatically allocate HTTP port from range 4242-5242, trying preferred port first then incrementing.

**Rationale:**
- Satisfies FR-002 (automatic port allocation)
- Eliminates manual configuration and port conflicts (NFR-R1)
- Range of 1000 ports supports high concurrency
- Simple algorithm: try, increment, repeat

**Alternatives Considered:**
- **Fixed Port:** Causes conflicts with multiple projects (current problem)
- **Random Port:** Less predictable, harder to debug
- **User Configuration:** Adds friction, violates zero-config goal

**Trade-offs:**
- **Pros:** Zero conflicts, zero configuration, predictable debugging
- **Cons:** Port exhaustion possible (but unlikely: 1000 ports)

#### Decision 3: State File for Discovery

**Decision:** Write JSON state file at `.agent-os/.mcp_server_state.json` with HTTP URL, PID, timestamp.

**Rationale:**
- Satisfies FR-003 (state file generation)
- Enables zero-config sub-agent discovery (NFR-U1)
- Simple, cross-platform, human-readable format
- Atomic write prevents corruption
- Includes PID for health checks

**Alternatives Considered:**
- **Environment Variables:** Not persistent across shells, hard to discover
- **Config File:** State is runtime-only, not configuration
- **Service Discovery (e.g., mDNS):** Over-engineering for localhost use case

**Trade-offs:**
- **Pros:** Simple, reliable, cross-platform, enables automation
- **Cons:** Stale files after crashes (mitigated by PID validation)

#### Decision 4: Dynamic Project Discovery

**Decision:** Discover project information at runtime via git commands and filesystem operations, never hardcode.

**Rationale:**
- Satisfies FR-004 (dynamic project discovery)
- Enables portability across machines and users
- Supports git and non-git projects
- Fresh data on every call

**Alternatives Considered:**
- **Hardcoded Project Name:** Breaks portability
- **User Configuration:** Adds manual step, can drift from reality
- **Package Metadata:** Not available for all projects

**Trade-offs:**
- **Pros:** Always accurate, zero configuration, portable
- **Cons:** Subprocess calls add minimal latency (~50ms)

#### Decision 5: Localhost-Only HTTP Binding

**Decision:** HTTP server binds to 127.0.0.1 only, never 0.0.0.0 or public interfaces.

**Rationale:**
- Satisfies NFR-S1 (security: localhost-only binding)
- Prevents network exposure without authentication
- Same trust model as stdio (local process only)
- Firewall provides additional protection layer

**Alternatives Considered:**
- **Network Binding with Auth:** Added complexity, out of scope for MVP
- **Unix Domain Sockets:** Windows compatibility issues, more complex discovery

**Trade-offs:**
- **Pros:** Simple, secure, consistent with stdio trust model
- **Cons:** No remote access (acceptable for current use cases)

### 1.3 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001 | TransportManager.run_dual_mode() | Orchestrates stdio (main thread) + HTTP (background thread) |
| FR-002 | PortManager.find_available_port() | Tries 4242, increments until available port found |
| FR-003 | PortManager.write_state() | Writes JSON to `.mcp_server_state.json` atomically |
| FR-004 | ProjectInfoDiscovery.get_project_info() | Runs git commands, reads filesystem dynamically |
| FR-005 | __main__.py CLI parser | Requires `--transport` arg, validates value |
| FR-006 | TransportManager.run_stdio_mode() | Runs stdio-only, preserves existing behavior |
| FR-007 | TransportManager.run_http_mode() | Runs HTTP-only in main thread |
| FR-008 | Single FastMCP instance | Both transports register all tools, no filtering |
| FR-009 | get_server_info() tool | Calls ProjectInfoDiscovery, returns metadata |
| FR-010 | __main__.py finally block | Cleans up state file, stops threads, releases port |
| FR-011 | Thread-safe components | RAGEngine/WorkflowEngine use threading locks |
| NFR-P1 | Socket binding test | Port check completes in < 1 second |
| NFR-S1 | HTTP server host="127.0.0.1" | Hardcoded localhost binding |
| NFR-R1 | Port allocation algorithm | 100% success within range 4242-5242 |

### 1.4 Technology Stack

**Runtime:**
- Language: Python 3.8+
- Virtual Environment: `.agent-os/venv/` (required for dependencies)

**Core Framework:**
- **FastMCP:** MCP server framework with stdio and HTTP transport support
- **MCP SDK:** Protocol implementation (for testing)

**Libraries:**
- **threading:** Concurrent transport handling (stdlib)
- **socket:** Port availability checking (stdlib)
- **subprocess:** Git command execution (stdlib)
- **json:** State file serialization (stdlib)
- **argparse:** CLI argument parsing (stdlib)
- **pathlib:** Path operations (stdlib)

**Dependencies (Existing):**
- lancedb: RAG vector index
- sentence-transformers: Embeddings
- watchdog: File watching
- playwright: Browser automation
- mistletoe: Markdown parsing

**Development:**
- pytest: Testing framework
- unittest.mock: Mocking
- mypy: Type checking

---

## 2. Component Design

### 2.1 Component: PortManager

**Purpose:** Manages dynamic HTTP port allocation and state file lifecycle.

**File:** `mcp_server/port_manager.py`

**Responsibilities:**
- Find available port in range 4242-5242
- Write state file atomically with comprehensive metadata
- Read state file for validation
- Clean up state file on shutdown
- Check port availability via socket binding

**Requirements Satisfied:**
- FR-002: Automatic port allocation
- FR-003: State file generation
- NFR-P1: Port allocation speed < 1 second
- NFR-R2: State file integrity

**Public Interface:**
```python
class PortManager:
    """Manages dynamic port allocation and state persistence."""
    
    DEFAULT_PORT_START = 4242
    DEFAULT_PORT_END = 5242
    STATE_FILE_NAME = ".mcp_server_state.json"
    
    def __init__(self, base_path: Path):
        """
        Initialize port manager.
        
        Args:
            base_path: Path to .agent-os directory
        """
        self.base_path = base_path
        self.state_file = base_path / self.STATE_FILE_NAME
        self.project_discovery = ProjectInfoDiscovery(base_path)
    
    def find_available_port(self, preferred_port: int = DEFAULT_PORT_START) -> int:
        """
        Find available port, trying preferred first.
        
        Algorithm:
        1. Try preferred_port (e.g., 4242)
        2. If taken, try preferred_port + 1, + 2, etc.
        3. Stop at DEFAULT_PORT_END or raise exception
        
        Args:
            preferred_port: Port to try first (default 4242)
            
        Returns:
            Available port number
            
        Raises:
            RuntimeError: If no ports available in range
        """
        for port in range(preferred_port, self.DEFAULT_PORT_END + 1):
            if self._is_port_available(port):
                return port
        
        raise RuntimeError(
            f"No available ports in range {preferred_port}-{self.DEFAULT_PORT_END}. "
            f"Close some Cursor windows and retry."
        )
    
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
          "version": "1.0.0",
          "transport": "dual",
          "port": 4243,
          "host": "127.0.0.1",
          "path": "/mcp",
          "url": "http://127.0.0.1:4243/mcp",
          "pid": 12345,
          "started_at": "2025-10-11T10:30:00Z",
          "project": {"name": "...", "root": "..."}
        }
        
        Args:
            transport: Transport mode ("dual", "stdio", "http")
            port: HTTP port (None for stdio-only)
            host: HTTP host (default "127.0.0.1")
            path: HTTP path (default "/mcp")
        """
        import os
        from datetime import datetime, timezone
        
        # Discover project info dynamically
        project_info = self.project_discovery.get_project_info()
        
        state = {
            "version": "1.0.0",
            "transport": transport,
            "port": port,
            "host": host,
            "path": path,
            "url": f"http://{host}:{port}{path}" if port else None,
            "pid": os.getpid(),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "project": {
                "name": project_info["name"],
                "root": project_info["root"]
            }
        }
        
        # Atomic write (temp + rename)
        temp_file = self.state_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
        temp_file.rename(self.state_file)
        
        # Set permissions (owner read/write only)
        self.state_file.chmod(0o600)
    
    @classmethod
    def read_state(cls, base_path: Path) -> Optional[Dict]:
        """
        Read server state (for sub-agents).
        
        Args:
            base_path: Path to .agent-os directory
            
        Returns:
            State dict or None if not found/invalid
        """
        state_file = base_path / cls.STATE_FILE_NAME
        
        if not state_file.exists():
            return None
        
        try:
            return json.loads(state_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    
    def cleanup_state(self) -> None:
        """Remove state file on shutdown."""
        if self.state_file.exists():
            self.state_file.unlink()
    
    def _is_port_available(self, port: int) -> bool:
        """Check if port is available by attempting bind."""
        import socket
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", port))
                return True
        except OSError:
            return False
```

**Dependencies:**
- Requires: `ProjectInfoDiscovery` (for project metadata)
- Provides: Port numbers, state file for sub-agents

**Error Handling:**
- Port exhaustion → Raise RuntimeError with actionable message
- State file write failure → Propagate exception (fatal)
- State file read corruption → Return None (graceful degradation)

### 2.2 Component: ProjectInfoDiscovery

**Purpose:** Dynamically discover project metadata without hardcoding.

**File:** `mcp_server/project_info.py`

**Responsibilities:**
- Determine project name from git repo or directory
- Discover project root path from filesystem
- Retrieve git information via subprocess calls
- Provide graceful fallbacks for non-git projects

**Requirements Satisfied:**
- FR-004: Dynamic project discovery
- FR-009: Server info discovery tool (data source)
- NFR-U1: Zero-configuration (no hardcoded values)

**Public Interface:**
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

        Args:
            base_path: Path to .agent-os directory
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

        Returns:
            Project information dict:
            {
                "name": str,
                "root": str,
                "agent_os_path": str,
                "git": {...} | None
            }
        """
        return {
            "name": self._get_project_name(),
            "root": str(self.project_root),
            "agent_os_path": str(self.base_path),
            "git": self._get_git_info(),
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

        Returns:
            Project name (NEVER hardcoded)
        """
        git_name = self._get_git_repo_name()
        if git_name:
            return git_name
        
        return self.project_root.name

    def _get_git_repo_name(self) -> Optional[str]:
        """
        Extract repository name from git remote URL.

        Returns:
            Repo name or None if not a git repo
        """
        remote = self._get_git_remote()
        if not remote:
            return None
        
        # Extract name from various URL formats
        # git@github.com:user/repo.git → repo
        # https://github.com/user/repo.git → repo
        import re
        match = re.search(r'/([^/]+?)(?:\.git)?$', remote)
        if match:
            return match.group(1)
        
        return None

    def _get_git_info(self) -> Optional[Dict]:
        """
        Get git repository information dynamically.

        Runs git commands:
        - git remote get-url origin
        - git branch --show-current
        - git rev-parse HEAD
        - git status --porcelain

        Returns:
            Git info dict or None if not a git repo
        """
        if not self._is_git_repo():
            return None

        return {
            "remote": self._get_git_remote(),
            "branch": self._get_git_branch(),
            "commit": self._get_git_commit(),
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
- Find .agent-os directory
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
        # 3. Find and validate .agent-os directory
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

**File:** `.agent-os/.mcp_server_state.json`

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
    "name": "agent-os-enhanced",
    "root": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced"
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
    "name": "agent-os-enhanced",
    "root": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced"
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

**File:** `.agent-os/config.yaml`

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
    
    discovery = ProjectInfoDiscovery(tmp_path / ".agent-os")
    info = discovery.get_project_info()
    
    assert info["name"] == "my-project"

def test_project_name_fallback_to_directory():
    """Should use directory name if not a git repo."""
    tmp_path = Path("/tmp/my-project")
    discovery = ProjectInfoDiscovery(tmp_path / ".agent-os")
    
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
    )
    
    # Wait for state file
    state = wait_for_state_file(test_project_path / ".agent-os")
    
    # Test HTTP endpoint
    async with streamablehttp_client(state["url"]) as (read, write, get_session_id):
        async with ClientSession(read, write) as session:
            result = await session.initialize()
            assert result.serverInfo.name == "agent-os-rag"
            
            tools = await session.list_tools()
            assert len(tools.tools) > 0
    
    # Test stdio
    proc.stdin.write(b'{"jsonrpc":"2.0","method":"tools/list","id":1}\n')
    proc.stdin.flush()
    line = proc.stdout.readline()
    result = json.loads(line)
    assert "result" in result
    
    # Cleanup
    proc.terminate()
```

**Multi-Project:**
```python
@pytest.mark.integration
def test_multiple_projects_no_conflicts():
    """Multiple projects should get different ports."""
    
    # Start 3 servers
    servers = []
    for project in [project_a, project_b, project_c]:
        proc = start_server(project, transport="http")
        servers.append(proc)
    
    # Read state files
    state_a = read_state(project_a / ".agent-os")
    state_b = read_state(project_b / ".agent-os")
    state_c = read_state(project_c / ".agent-os")
    
    # All should have different ports
    ports = {state_a["port"], state_b["port"], state_c["port"]}
    assert len(ports) == 3
    
    # All should be accessible
    assert is_server_responding(state_a["url"])
    assert is_server_responding(state_b["url"])
    assert is_server_responding(state_c["url"])
    
    # Cleanup
    for proc in servers:
        proc.terminate()
```

### 7.3 Thread Safety Tests

```python
@pytest.mark.integration
def test_concurrent_stdio_and_http_requests():
    """Concurrent requests from both transports should work."""
    
    # Start server in dual mode
    server = start_dual_mode_server()
    
    # Function to call via stdio
    def call_stdio():
        results = []
        for _ in range(100):
            result = server.call_stdio("search_standards", {"query": "test"})
            results.append(result)
        return results
    
    # Function to call via HTTP
    async def call_http():
        results = []
        for _ in range(100):
            result = await server.call_http("search_standards", {"query": "test"})
            results.append(result)
        return results
    
    # Run concurrently
    with ThreadPoolExecutor() as executor:
        stdio_future = executor.submit(call_stdio)
        http_future = executor.submit(lambda: asyncio.run(call_http()))
        
        stdio_results = stdio_future.result()
        http_results = http_future.result()
    
    # All requests should succeed
    assert len(stdio_results) == 100
    assert len(http_results) == 100
    
    # Results should be identical (same RAG index)
    assert stdio_results[0] == http_results[0]
```

### 7.4 Error Scenario Tests

```python
def test_port_exhaustion_error_message():
    """Should provide actionable error when ports exhausted."""
    # Bind all ports 4242-5242 (or mock)
    
    with pytest.raises(RuntimeError) as exc_info:
        pm = PortManager(tmp_path)
        pm.find_available_port(4242)
    
    assert "No available ports" in str(exc_info.value)
    assert "Close some Cursor windows" in str(exc_info.value)

def test_stale_state_file_detection():
    """Sub-agent should detect stale state file."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    state = PortManager.read_state(tmp_path)
    
    # Simulate server crash (PID no longer exists)
    state["pid"] = 99999  # Non-existent PID
    
    assert not is_process_alive(state["pid"])
    # Sub-agent should not attempt connection

def test_http_startup_failure():
    """Should cleanup state file if HTTP fails to start."""
    # Mock FastMCP to raise exception on HTTP start
    
    with pytest.raises(RuntimeError):
        # Attempt to start server
        pass
    
    # State file should be cleaned up
    assert not (tmp_path / ".mcp_server_state.json").exists()
```

### 7.5 Test Coverage Goals

- **Unit Tests:** 90%+ coverage for new components
- **Integration Tests:** All transport modes, multi-project scenarios
- **Thread Safety:** Concurrent request testing
- **Error Scenarios:** Port exhaustion, crashes, corrupted state

---

## 8. Requirements Traceability Matrix

| Requirement ID | Component(s) | Test Coverage |
|----------------|--------------|---------------|
| FR-001 | TransportManager.run_dual_mode() | test_dual_transport_serves_both |
| FR-002 | PortManager.find_available_port() | test_find_available_port_* |
| FR-003 | PortManager.write_state() | test_write_state_* |
| FR-004 | ProjectInfoDiscovery.get_project_info() | test_project_name_* |
| FR-005 | __main__.py CLI parser | test_cli_arguments |
| FR-006 | TransportManager.run_stdio_mode() | test_stdio_only_mode |
| FR-007 | TransportManager.run_http_mode() | test_http_only_mode |
| FR-008 | Single FastMCP instance | test_tool_parity_across_transports |
| FR-009 | get_server_info() tool | test_get_server_info_tool |
| FR-010 | __main__.py finally block | test_graceful_shutdown |
| FR-011 | RAGEngine/WorkflowEngine locks | test_concurrent_stdio_and_http_requests |
| NFR-P1 | PortManager performance | test_port_allocation_performance |
| NFR-P2 | HTTP startup timeout | test_http_ready_within_5_seconds |
| NFR-P3 | Thread-safe components | test_concurrent_requests_no_degradation |
| NFR-S1 | HTTP host="127.0.0.1" | test_localhost_only_binding |
| NFR-S2 | State file chmod(0o600) | test_state_file_permissions |
| NFR-R1 | Port allocation algorithm | test_multiple_projects_no_conflicts |
| NFR-R2 | Atomic state write | test_write_state_atomic |

---

## 9. Dependencies and Assumptions

### 9.1 External Dependencies

**Required:**
- FastMCP: MCP server framework (existing)
- Python 3.8+: Threading, subprocess, socket
- MCP SDK: Testing HTTP transport (dev dependency)

**No New Dependencies:**
All new functionality uses Python stdlib (threading, socket, subprocess, json, pathlib)

### 9.2 Assumptions

1. **FastMCP Dual Transport:** Single FastMCP instance can serve both stdio and HTTP (VALIDATED with working code)
2. **IDE stdio Support:** Cursor, Windsurf, Claude Desktop support stdio transport (confirmed)
3. **Port Availability:** Range 4242-5242 not blocked by firewalls (typical environment)
4. **Filesystem Access:** Sub-agents can read .agent-os/.mcp_server_state.json (same user)
5. **Python Threading:** Sufficient for concurrent stdio + HTTP handling (proven stable)
6. **Git Availability:** Git commands available for project discovery (fallback to directory name)

---

## 10. Migration and Rollout

### 10.1 Backward Compatibility

**No Breaking Changes:**
- Existing stdio-only mode preserved: `--transport stdio`
- All tools and features work identically
- Configuration file fully backward compatible

**Opt-In:**
- Dual transport is opt-in via `--transport dual` argument
- Users can continue using stdio-only indefinitely

### 10.2 Rollout Plan

**Phase 1: Core Implementation (Week 1)**
- Implement PortManager, ProjectInfoDiscovery, TransportManager
- Update __main__.py
- Unit tests

**Phase 2: Integration Testing (Week 1-2)**
- Dual transport tests
- Multi-project tests
- Thread safety tests

**Phase 3: Sub-Agent Integration (Week 2)**
- Example sub-agent client
- Documentation for sub-agent developers

**Phase 4: Documentation (Week 2-3)**
- Update README
- Sub-agent integration guide
- Troubleshooting section

**Phase 5: Rollout (Week 3)**
- Merge to main
- Announce in changelog
- Monitor for issues

---

## 11. Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-11 | 1.0 | Initial technical specifications | Agent OS Team |

