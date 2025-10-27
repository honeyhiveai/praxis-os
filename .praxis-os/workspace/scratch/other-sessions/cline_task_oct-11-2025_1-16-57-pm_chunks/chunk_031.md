        assert is_server_responding(state_b["url"])
        assert is_server_responding(state_c["url"])
        
    finally:
        # Cleanup
        for proc in servers:
            proc.terminate()
            proc.wait(timeout=5)

def is_server_responding(url: str) -> bool:
    """Check if server responds to HTTP requests."""
    import requests
    
    try:
        response = requests.post(
            url,
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            headers={"Accept": "application/json"},
            timeout=5
        )
        return response.status_code == 200
    except requests.RequestException:
        return False
```

### Thread Safety Testing

**Example: Concurrent Request Test**
```python
# tests/integration/test_thread_safety.py

@pytest.mark.integration
def test_concurrent_stdio_and_http_requests(running_server):
    """Concurrent requests from both transports should work."""
    
    # Function to call via stdio
    def call_stdio(count: int):
        results = []
        for i in range(count):
            result = running_server.call_stdio(
                "search_standards",
                {"query": f"test query {i}", "n_results": 5}
            )
            results.append(result)
        return results
    
    # Function to call via HTTP
    async def call_http(count: int):
        results = []
        async with streamablehttp_client(running_server.http_url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                for i in range(count):
                    result = await session.call_tool(
                        "search_standards",
                        arguments={"query": f"test query {i}", "n_results": 5}
                    )
                    results.append(result)
        return results
    
    # Run concurrently
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        stdio_future = executor.submit(call_stdio, 50)
        http_future = executor.submit(lambda: asyncio.run(call_http(50)))
        
        stdio_results = stdio_future.result()
        http_results = http_future.result()
    
    # All requests should succeed
    assert len(stdio_results) == 50
    assert len(http_results) == 50
    
    # Results should be consistent (same RAG index)
    assert stdio_results[0] == http_results[0]
```

---

## 5. Deployment

### Development Environment Setup

**Prerequisites:**
```bash
# Python 3.8+ required
python3 --version

# Virtual environment at .praxis-os/venv
cd /path/to/project
python3 -m venv .praxis-os/venv
source .praxis-os/venv/bin/activate

# Install dependencies
pip install -r mcp_server/requirements.txt
```

### Testing Before Deployment

```bash
# Run full test suite
pytest tests/

# Check code coverage
pytest --cov=mcp_server --cov-report=term-missing

# Run linter
mypy mcp_server/
flake8 mcp_server/

# Manual testing
python -m mcp_server --transport dual --log-level DEBUG
```

### Configuration Update

**Update .cursor/mcp.json:**
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
        "PYTHONPATH": "${workspaceFolder}/.praxis-os"
      },
      "transport": "stdio"
    }
  }
}
```

### Rollout Steps

1. **Merge to Main**
   ```bash
   git checkout main
   git pull
   git merge feature/dual-transport
   git push
   ```

2. **Tag Release**
   ```bash
   git tag -a v1.1.0 -m "Add dual-transport support"
   git push origin v1.1.0
   ```

3. **Update Documentation**
   - Update README with feature description
   - Update CHANGELOG with version notes
   - Add troubleshooting section

4. **Monitor for Issues**
   - Watch for error reports in first week
   - Check logs for unexpected errors
   - Respond to user questions promptly

### Rollback Procedure

If critical issues discovered:

1. **Immediate Rollback**
   ```bash
   git revert HEAD
   git push
   ```

2. **Notify Users**
   - Post announcement about rollback
   - Explain issue and timeline for fix

3. **Fix and Re-Deploy**
   - Fix issue in separate branch
   - Re-run full test suite
   - Re-deploy with caution

---

## 6. Troubleshooting

### Issue 1: "No available ports in range 4242-5242"

**Symptoms:**
- Server fails to start
- Error message about port exhaustion

**Cause:**
- 1000+ MCP servers running (unlikely)
- OR ports blocked by firewall/other services

**Solution:**
```bash
# Find MCP servers
ps aux | grep "mcp_server"

# Kill old servers
pkill -f "python -m mcp_server"

# Check what's using ports
lsof -i :4242-4244

# If other services using ports, update config.yaml
# to use different port range (future enhancement)
```

### Issue 2: "MCP server not responding"

**Symptoms:**
- Sub-agent can't connect
- HTTP endpoint unreachable

**Debug Steps:**
```bash
# 1. Check state file exists
cat .praxis-os/.mcp_server_state.json

# 2. Check server is running
ps aux | grep mcp_server

# 3. Validate PID
ps -p <PID_FROM_STATE_FILE>

# 4. Test HTTP endpoint manually
curl -X POST http://127.0.0.1:4243/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# 5. Check server logs
# (location depends on how server was started)
```

**Solution:**
- If PID invalid: Restart server (restart IDE or run manually)
- If port unreachable: Check firewall settings
- If corrupted state: Delete `.mcp_server_state.json` and restart

### Issue 3: "State file is stale"

**Symptoms:**
- State file exists but server not running
- Sub-agent gets connection refused

**Cause:**
- Server crashed without cleanup
- IDE killed process forcefully

**Solution:**
```bash
# Check if PID is valid
ps -p <PID_FROM_STATE_FILE>

# If process not found, delete stale state file
rm .praxis-os/.mcp_server_state.json

# Restart IDE or server manually
```

### Issue 4: "Port already in use"

**Symptoms:**
- Server fails to bind to port
- Error: "Address already in use"

**Cause:**
- Another process using ports 4242-5242
- Old MCP server didn't release port

**Solution:**
```bash
# Find what's using the ports
lsof -i :4242-5242

# Kill specific process if it's an old MCP server
kill <PID>

# OR wait a few seconds for port to be released
```

### Issue 5: "HTTP server failed to start within 5 seconds"

**Symptoms:**
- Server exits with timeout error
- Dual mode fails to initialize

**Cause:**
- System under heavy load
- Port binding delayed
- Network issues

**Solution:**
```bash
# Check system load
uptime

# Check available memory
free -h

# Try HTTP-only mode to isolate issue
python -m mcp_server --transport http --log-level DEBUG

# If successful, it's a stdio conflict (unlikely)
# If failed, it's an HTTP server issue

# Check firewall
sudo iptables -L -n | grep 4242
```

### Issue 6: "Thread safety errors"

**Symptoms:**
- Concurrent requests fail intermittently
- Race condition errors in logs

**Debug:**
```bash
# Enable debug logging
python -m mcp_server --transport dual --log-level DEBUG

# Run concurrent test
pytest tests/integration/test_thread_safety.py -v

# Check for deadlocks
# (look for threads waiting indefinitely)
```

**Solution:**
- Report issue with logs
- Temporarily use stdio-only mode
- Wait for fix in next release

### Issue 7: "Git command timeout"

**Symptoms:**
- Server takes long to start
- Logs show git command timeouts

**Cause:**
- Slow git operations
- Network issues with git remote

**Solution:**
```bash
# Test git commands manually
time git remote get-url origin
time git branch --show-current

# If slow, check network
ping github.com

# If not a git repo, no issue (falls back to directory name)
```

### Debug Commands Cheat Sheet

```bash
# Check server status
ps aux | grep mcp_server

# Check ports in use
lsof -i :4242-4244

# Test HTTP endpoint
curl -X POST http://127.0.0.1:4243/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Check state file
cat .praxis-os/.mcp_server_state.json | jq

# Kill all MCP servers
pkill -f "python -m mcp_server"

# Watch logs in real-time
python -m mcp_server --transport dual --log-level DEBUG 2>&1 | tee server.log
```

---

## 7. Best Practices Summary

### DO ✅

- Use `--transport dual` for development with sub-agents
- Check state file exists before sub-agent connection
- Validate PID before trusting state file
- Use atomic writes for state file
- Add threading locks for shared components
- Log clearly at INFO level for user visibility
- Provide actionable error messages
- Test thread safety with concurrent requests
- Document all assumptions in code comments

### DON'T ❌

- Don't hardcode project names or paths
- Don't bind to 0.0.0.0 (security risk)
- Don't skip health check for HTTP server
- Don't silently fail on errors
- Don't use broad exception catching (except Exception)
- Don't forget cleanup in finally blocks
- Don't assume port 4242 is available
- Don't start stdio before HTTP is ready
- Don't modify state file after creation

---

## 8. Quick Reference

### CLI Commands

```bash
# Dual transport (recommended)
python -m mcp_server --transport dual

# stdio-only (backward compatible)
python -m mcp_server --transport stdio

# HTTP-only (standalone)
python -m mcp_server --transport http

# Debug mode
python -m mcp_server --transport dual --log-level DEBUG
```

### State File Location

```
.praxis-os/.mcp_server_state.json
```

### Default Port Range

```
4242 - 5242 (1000 ports)
```

### Key Files

```
mcp_server/port_manager.py       # Port allocation
mcp_server/project_info.py       # Project discovery
mcp_server/transport_manager.py  # Transport orchestration
mcp_server/__main__.py           # Entry point
.cursor/mcp.json                 # IDE configuration
```

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-11 | 1.0 | Initial implementation guidance | Agent OS Team |


</file_content>

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport/specs.md">
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
│  MCP Server Process (.praxis-os/venv/bin/python)                 │
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
│  │ State File: .praxis-os/.mcp_server_state.json            │  │
│  │   {transport, port, url, pid, project}                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP: http://127.0.0.1:4243/mcp
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Sub-Agents (Cline, Aider, Custom)                              │
│  1. Read .praxis-os/.mcp_server_state.json                      │
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

**Decision:** Write JSON state file at `.praxis-os/.mcp_server_state.json` with HTTP URL, PID, timestamp.

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
- Virtual Environment: `.praxis-os/venv/` (required for dependencies)

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
            base_path: Path to .praxis-os directory
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
            base_path: Path to .praxis-os directory
            
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
            base_path: Path to .praxis-os directory
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
