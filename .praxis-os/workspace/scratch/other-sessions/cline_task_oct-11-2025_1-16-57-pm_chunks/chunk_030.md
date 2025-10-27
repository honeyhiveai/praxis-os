        for project_name, conn in self.connections.items():
            results[project_name] = conn.call_tool("search_standards", {...})
```

This enables persona systems working across multiple projects!

---

### 5. 🔒 Why Dynamic Discovery Matters

**Problem with hardcoding:**
```python
# BAD: Hardcoded values
PROJECT_NAME = "praxis-os"
PROJECT_ROOT = "/Users/josh/src/..."

# Breaks when:
# - Different user
# - Different path
# - Forked repo
# - Renamed directory
```

**Solution - Dynamic discovery:**
```python
# GOOD: Runtime discovery
name = _get_git_repo_name()  # subprocess: git remote get-url origin
if not name:
    name = self.project_root.name  # fallback: directory name

# Works everywhere:
# - Any user
# - Any path
# - Any fork
# - Any directory name
```

---

### 6. 🎨 Complete Architecture Flow

**Discovery flow now includes project info:**

```
Server Startup:
  ├─ ProjectInfoDiscovery(base_path)
  │   ├─ Run git commands
  │   │   └─ Extract: "praxis-os"
  │   ├─ Determine paths from filesystem
  │   └─ Cache discovery service
  │
  ├─ PortManager.write_state()
  │   ├─ project_discovery.get_project_info()  ← DYNAMIC
  │   └─ Write state file with project info
  │
  └─ register_tools(project_discovery=...)
      └─ get_server_info() tool registered

Client Connects:
  ├─ Read state file
  │   └─ Quick check: project name matches?
  │
  ├─ Connect via HTTP
  │
  ├─ Call get_server_info()
  │   ├─ Fresh git info (current branch/commit)
  │   ├─ Runtime capabilities
  │   └─ Server uptime/status
  │
  └─ Verify project, display info in UI
```

---

### What I Like About the Updates

**1. Validation First**
- They didn't just design it - they TESTED it
- Used official MCP SDK (not custom code)
- Proved the core assumption before full implementation
- Reduced risk significantly

**2. Real Use Cases**
- Multi-project agent example is practical
- Client verification solves actual UX problems
- Discovery pattern handles edge cases (no git, different paths)

**3. No Hardcoding**
- Everything discovered at runtime
- Works in any environment
- Transferable across forks/renames
- Proper engineering practice

**4. Complete Integration**
- ProjectInfoDiscovery wired through dependency injection
- State file enhanced but backward compatible
- New MCP tool follows best practices
- Clean separation of concerns

---

### Implementation Readiness

**Before (original doc):**
- Theoretical design
- Unvalidated assumptions
- "Needs testing"

**Now (updated doc):**
- ✅ Core architecture validated
- ✅ Working proof-of-concept code
- ✅ Tested with official MCP SDK  
- ✅ Project discovery designed and integrated
- ✅ Ready for production implementation

**Remaining work:**
1. Implement PortManager (straightforward)
2. Implement TransportManager (pattern proven)
3. Implement ProjectInfoDiscovery (design complete)
4. Wire into __main__.py (clear plan)
5. Integration tests (test framework ready)

---

### My Assessment

**The updated design is excellent:**

✅ **Validated** - Core assumptions tested and proven  
✅ **Complete** - Project discovery adds missing piece  
✅ **Practical** - Real use cases and examples  
✅ **Production-ready** - No theoretical blockers  
✅ **Well-documented** - Implementation details clear  

**The Cursor agent did thorough work:**
- Actually ran experiments to validate
- Used official MCP SDK (not custom)
- Added missing functionality (project discovery)
- Thought through real use cases (multi-project)
- Provided working code examples

**Ready to implement this design!**

The dual-transport architecture is proven, the project discovery solves the verification problem, and all the pieces are in place for production deployment.

**What's next?** Implement according to the validated design!
</result>
<task_progress>
- [x] Read updated design document
- [x] Identified key changes vs original
- [x] Analyzed validation results
- [x] Reviewed ProjectInfoDiscovery addition
- [x] Assessed production readiness
- [x] Ready to help implement validated design
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
take a look at the spec we generated for this work '.praxis-os/specs/2025-10-11-mcp-dual-transport' (see below for file content)
</feedback>

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport">
├── README.md
├── implementation.md
├── specs.md
├── srd.md
├── supporting-docs/
└── tasks.md

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport/README.md">
# MCP Server Dual-Transport Architecture

**Status:** ✅ Design Complete - Ready for Implementation  
**Date:** October 11, 2025  
**Version:** 1.0  

---

## Executive Summary

This specification defines a dual-transport architecture for the Agent OS MCP server that enables:

1. **Primary IDE integration** via stdio transport (Cursor, Windsurf, Claude Desktop)
2. **Sub-agent access** via HTTP transport (Cline, Aider, custom agents)
3. **Multi-project isolation** with automatic port allocation
4. **Zero-conflict deployment** across multiple Cursor windows

### Key Benefits

✅ **Single server serves multiple agents** - IDE + sub-agents access same RAG/tools/state  
✅ **Automatic port allocation** - No conflicts when multiple projects open  
✅ **Project isolation** - Each project has independent server  
✅ **Zero-configuration sub-agents** - Discover server via state file  
✅ **IDE agnostic** - Works with any MCP-compatible IDE  

### Validation Status

This design has been **completely validated** with working code and real MCP SDK testing:
- ✅ Dual transport proven (stdio + HTTP simultaneously)
- ✅ Tool calls validated via HTTP using MCP SDK client
- ✅ Same FastMCP instance serves both transports
- ✅ Working implementation provided
- ✅ Ready for production implementation

---

## Quick Links

- **Requirements:** [srd.md](srd.md)
- **Technical Design:** [specs.md](specs.md)
- **Implementation Tasks:** [tasks.md](tasks.md)
- **Implementation Guide:** [implementation.md](implementation.md)

---

## Current Situation

### Problems Solved

1. **Single Transport Model**
   - Current implementation uses only HTTP or only stdio
   - Can't serve both IDE (stdio) and sub-agents (HTTP) simultaneously

2. **Port Conflicts**
   - Multiple Agent OS instances (different Cursor windows) conflict on port 4242
   - No mechanism to allocate different ports per project

3. **Sub-Agent Access**
   - Sub-agents (Cline, Aider) run in different environments/venvs
   - Need network access to shared MCP server

---

## Solution Overview

### Architecture Principles

- **Explicit transport mode** (user-controlled via CLI flag)
- **Automatic port allocation** (system-controlled, conflict-free)
- **Project isolation** (separate state per project)
- **Single venv requirement** (agent-os dependencies only)

### Transport Modes

1. **Dual Mode** (stdio + HTTP)
   - Main thread: stdio for IDE
   - Background thread: HTTP for sub-agents
   - State file includes HTTP URL for discovery

2. **stdio-only Mode**
   - IDE integration without sub-agents
   - No HTTP server, no port allocation

3. **HTTP-only Mode**
   - Standalone server, all agents via HTTP
   - Can run as system service

---

## Impact Summary

### Changes Required

**New Components:**
- `mcp_server/port_manager.py` - Port allocation and state management
- `mcp_server/project_info.py` - Dynamic project discovery
- `.praxis-os/.mcp_server_state.json` - Runtime state file (gitignored)

**Modified Components:**
- `mcp_server/__main__.py` - Add CLI args, transport orchestration
- `.cursor/mcp.json` - Add `--transport dual` argument
- `.gitignore` - Add state file

**No Breaking Changes:**
- Existing stdio-only mode still works (`--transport stdio`)
- All existing tools/features preserved
- Backward compatible with current deployments

---

## For Implementers

1. Read [srd.md](srd.md) for requirements context
2. Review [specs.md](specs.md) for technical design
3. Follow [tasks.md](tasks.md) for implementation sequence
4. Reference [implementation.md](implementation.md) for patterns

---

## Questions or Feedback

**For implementation questions:** See [implementation.md](implementation.md)  
**For requirements clarification:** See [srd.md](srd.md)  
**For design questions:** See [specs.md](specs.md)

---

## Timeline

- **Week 1:** Implementation (port manager, transport manager, entry point updates)
- **Week 1-2:** Testing (integration tests, multi-project tests)
- **Week 2:** Sub-agent integration (discovery utility, examples)
- **Week 2-3:** Documentation
- **Week 3:** Rollout

**Total Estimated Effort:** 20-27 hours (2.5-3.5 days)

---

## Success Criteria

✅ Multiple Cursor windows can open with Agent OS without conflicts  
✅ Sub-agents discover and connect to MCP server with zero configuration  
✅ All existing tools work identically on both stdio and HTTP transports  
✅ State file accurately reflects server status and enables discovery  
✅ Graceful shutdown cleans up state file reliably  
✅ Zero breaking changes for existing stdio-only users  
✅ Test coverage ≥ 80% for all new components  
✅ Documentation updated with dual-transport setup instructions  
✅ At least one sub-agent example (Cline or custom) demonstrated

---

## Supporting Documentation

This specification was created from:
- [DESIGN-DOC-MCP-Dual-Transport.md](supporting-docs/DESIGN-DOC-MCP-Dual-Transport.md) - Complete architectural design with validation

See [supporting-docs/INSIGHTS.md](supporting-docs/INSIGHTS.md) for extracted insights (45 total).

---

## Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-11 | 1.0 | Initial specification created via spec_creation_v1 workflow | Agent OS Team |

</file_content>

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport/implementation.md">
# Implementation Approach

**Project:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11

---

## 1. Implementation Philosophy

### Core Principles

1. **Explicit Over Implicit**
   - User explicitly specifies transport mode via `--transport` CLI flag
   - No magic defaults or auto-detection
   - Clear logging of what mode is active

2. **Zero-Configuration Automation**
   - Port allocation is automatic (no manual config)
   - Project discovery is dynamic (no hardcoding)
   - Sub-agents discover server via state file (no manual URL entry)

3. **Fail-Fast with Actionable Errors**
   - Port exhaustion shows clear error with solution
   - HTTP startup failure prevents partial initialization
   - Stale state files detectable via PID validation

4. **Project Isolation**
   - Each project has independent server, port, state, RAG index
   - No shared state between projects
   - Complete isolation prevents cross-contamination

5. **Thread Safety**
   - All shared components protected with threading locks
   - FastMCP handles I/O asynchronously (uvicorn ASGI)
   - Tested with concurrent requests from both transports

6. **Backward Compatibility**
   - stdio-only mode preserved for existing users
   - All existing tools work identically
   - Zero breaking changes, opt-in only

---

## 2. Implementation Order

Follow the phase sequence from [tasks.md](tasks.md):

### Phase 1: Core Components (8-10 hours)
1. ✅ PortManager - Port allocation and state management
2. ✅ ProjectInfoDiscovery - Dynamic project metadata
3. ✅ TransportManager - Transport orchestration
4. ✅ Update __main__.py - CLI and lifecycle
5. ✅ Configuration schema updates
6. ✅ get_server_info tool
7. ✅ .gitignore updates

### Phase 2: Testing (6-8 hours)
1. ✅ Unit tests for all new components
2. ✅ Integration tests for dual transport
3. ✅ Multi-project testing
4. ✅ Error scenario testing
5. ✅ Thread safety validation

### Phase 3: Documentation (4-6 hours)
1. ✅ Sub-agent discovery utility
2. ✅ Example sub-agent client
3. ✅ IDE configuration updates
4. ✅ README and guides
5. ✅ Troubleshooting documentation

### Phase 4: Rollout (2-3 hours)
1. ✅ Pre-merge validation
2. ✅ Merge and tag release
3. ✅ Update installation instructions
4. ✅ Announce and monitor

---

## 3. Code Patterns

### Pattern 1: Port Allocation with Error Handling

**Good Pattern:**
```python
class PortManager:
    """Manages port allocation with clear error handling."""
    
    DEFAULT_PORT_START = 4242
    DEFAULT_PORT_END = 5242
    
    def find_available_port(self, preferred_port: int = DEFAULT_PORT_START) -> int:
        """
        Find available port with early exit.
        
        :raises RuntimeError: With actionable error message
        """
        for port in range(preferred_port, self.DEFAULT_PORT_END + 1):
            if self._is_port_available(port):
                logger.info(f"Allocated port {port}")
                return port  # Early exit on first available
        
        # Actionable error message
        raise RuntimeError(
            f"No available ports in range {preferred_port}-{self.DEFAULT_PORT_END}. "
            f"Close some Cursor windows and retry."
        )
    
    def _is_port_available(self, port: int) -> bool:
        """Fast socket binding test."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(("127.0.0.1", port))
                return True
        except OSError:
            return False  # Immediately try next port
```

**Anti-Pattern:**
```python
# DON'T: Vague error without guidance
def find_port():
    for port in range(4242, 5242):
        if port_available(port):
            return port
    raise Exception("No ports")  # BAD: No actionable guidance
```

### Pattern 2: Atomic State File Writing

**Good Pattern:**
```python
def write_state(self, transport: str, port: Optional[int], ...) -> None:
    """Atomic write prevents corruption."""
    
    # Gather all data first
    state = {
        "version": "1.0.0",
        "transport": transport,
        "port": port,
        # ... all fields ...
    }
    
    # Atomic write: temp file + rename
    temp_file = self.state_file.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temp_file.rename(self.state_file)  # Atomic on POSIX
    
    # Set restrictive permissions
    self.state_file.chmod(0o600)  # Owner read/write only
    
    logger.info(f"State file written: {self.state_file}")
```

**Anti-Pattern:**
```python
# DON'T: Direct write (can corrupt on crash)
def write_state(self, data):
    with open(STATE_FILE, "w") as f:
        f.write(json.dumps(data))  # BAD: Not atomic
```

### Pattern 3: Dynamic Discovery Without Hardcoding

**Good Pattern:**
```python
class ProjectInfoDiscovery:
    """All discovery is runtime, no hardcoding."""
    
    def _get_project_name(self) -> str:
        """Dynamic name from git or directory."""
        # Try git repository name first
        git_name = self._get_git_repo_name()
        if git_name:
            return git_name  # From git remote URL
        
        # Fallback to directory name
        return self.project_root.name  # From filesystem
    
    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """Run git command with timeout and error handling."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=5  # Prevent hanging
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
            return None  # Graceful degradation
```

**Anti-Pattern:**
```python
# DON'T: Hardcode project info
def get_project_info():
    return {
        "name": "praxis-os",  # BAD: Hardcoded
        "root": "/Users/josh/projects/agent-os"  # BAD: Machine-specific
    }
```

### Pattern 4: Thread-Safe Dual Transport

**Good Pattern:**
```python
class TransportManager:
    """Orchestrate stdio + HTTP with proper synchronization."""
    
    def run_dual_mode(self, http_host: str, http_port: int, http_path: str) -> None:
        """Dual mode with health check before stdio."""
        logger.info("🔄 Starting dual transport mode")
        
        # Start HTTP in background daemon thread
        self.http_thread = self._start_http_thread(http_host, http_port, http_path)
        
        # Wait for HTTP ready (health check)
        if not self._wait_for_http_ready(http_host, http_port, timeout=5):
            raise RuntimeError(
                "HTTP server failed to start within 5 seconds. "
                "Check logs for details."
            )
        
        logger.info("✅ HTTP transport ready")
        logger.info("🔌 Starting stdio transport (blocking)")
        
        # Run stdio in main thread (blocks until shutdown)
        self.mcp_server.run(transport="stdio", show_banner=False)
    
    def _start_http_thread(self, host: str, port: int, path: str) -> threading.Thread:
        """Start HTTP server in daemon thread."""
        def run_http():
            try:
                self.mcp_server.run(
                    transport="streamable-http",
                    host=host,
                    port=port,
                    path=path,
                    show_banner=False
                )
            except Exception as e:
                logger.error(f"HTTP transport error: {e}", exc_info=True)
        
        thread = threading.Thread(
            target=run_http,
            daemon=True,  # Dies with main thread
            name="http-transport"
        )
        thread.start()
        return thread
    
    def _wait_for_http_ready(self, host: str, port: int, timeout: int = 5) -> bool:
        """Poll socket connection until ready or timeout."""
        import time
        
        start = time.time()
        while time.time() - start < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    sock.connect((host, port))
                    return True  # Connection successful
            except (ConnectionRefusedError, OSError):
                time.sleep(0.5)  # Wait before retry
        
        return False  # Timeout
```

**Anti-Pattern:**
```python
# DON'T: Start stdio before HTTP is ready
def run_dual_mode(self, host, port, path):
    # Start HTTP (no health check)
    threading.Thread(target=lambda: self.mcp.run(host=host, port=port)).start()
    
    # Immediately start stdio (HTTP might not be ready!)
    self.mcp.run(transport="stdio")  # BAD: Race condition
```

### Pattern 5: Graceful Shutdown with Cleanup

**Good Pattern:**
```python
def main() -> None:
    """Entry point with comprehensive cleanup."""
    try:
        # Initialization
        port_manager = PortManager(base_path)
        transport_mgr = TransportManager(mcp, config)
        
        # Write state file
        port_manager.write_state(transport="dual", port=http_port, ...)
        
        # Run server (blocks)
        transport_mgr.run_dual_mode(http_host, http_port, http_path)
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # ALWAYS cleanup
        if 'port_manager' in locals():
            port_manager.cleanup_state()
        if 'transport_mgr' in locals():
            transport_mgr.shutdown()
        
        logger.info("Shutdown complete")
```

**Anti-Pattern:**
```python
# DON'T: Forget cleanup
def main():
    port_manager = PortManager()
    port_manager.write_state(...)
    
    mcp.run(transport="stdio")  # BAD: No try/finally, state file orphaned
```

### Pattern 6: Thread-Safe Component Access

**Good Pattern:**
```python
class RAGEngine:
    """Thread-safe RAG query engine."""
    
    def __init__(self):
        self._query_lock = threading.Lock()
        self._index = self._load_index()
    
    def query(self, text: str, n_results: int = 5) -> List[Result]:
        """Thread-safe query with lock."""
        with self._query_lock:
            # Critical section: only one thread queries at a time
            results = self._search(text, n_results)
            return results
    
    def _search(self, text: str, n_results: int) -> List[Result]:
        """Internal search (called within lock)."""
        embedding = self._embed(text)
        return self._index.search(embedding, n_results)
```

**Anti-Pattern:**
```python
# DON'T: No thread safety for shared state
class RAGEngine:
    def query(self, text):
        # BAD: Multiple threads can access _index concurrently
        return self._index.search(text)  # Potential race condition
```

### Pattern 7: CLI Argument Parsing with Validation

**Good Pattern:**
```python
def main() -> None:
    """Entry point with explicit argument parsing."""
    parser = argparse.ArgumentParser(
        description="Agent OS MCP Server with dual-transport support"
    )
    parser.add_argument(
        "--transport",
        choices=["dual", "stdio", "http"],
        required=True,  # Explicit choice required
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
    
    # Log chosen mode clearly
    logger.info("=" * 60)
    logger.info("Agent OS MCP Server")
    logger.info(f"Transport Mode: {args.transport}")
    logger.info("=" * 60)
```

**Anti-Pattern:**
```python
# DON'T: Implicit defaults or magic detection
def main():
    transport = "stdio"  # BAD: Default hidden from user
    if os.environ.get("ENABLE_HTTP"):  # BAD: Magic behavior
        transport = "dual"
```

---

## 4. Testing Strategy

### Unit Testing Approach

**Philosophy:**
- Test each component in isolation
- Mock external dependencies
- Fast execution (< 5 seconds total)
- Coverage ≥ 80%

**Example: PortManager Tests**
```python
# tests/unit/test_port_manager.py

import pytest
import socket
from pathlib import Path
from unittest.mock import Mock, patch

from mcp_server.port_manager import PortManager

def test_find_available_port_prefers_first(tmp_path):
    """Should use preferred port if available."""
    pm = PortManager(tmp_path)
    port = pm.find_available_port(preferred_port=9000)
    
    assert port == 9000

def test_find_available_port_increments_if_taken(tmp_path):
    """Should increment if preferred port taken."""
    # Bind port 9000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 9000))
    
    try:
        pm = PortManager(tmp_path)
        port = pm.find_available_port(preferred_port=9000)
        
        # Should skip 9000 and use 9001
        assert port == 9001
    finally:
        sock.close()

def test_find_available_port_exhaustion(tmp_path):
    """Should raise RuntimeError with actionable message."""
    pm = PortManager(tmp_path)
    pm.DEFAULT_PORT_END = 9002  # Small range for testing
    
    # Bind all ports in range
    sockets = []
    for port in range(9000, 9003):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", port))
        sockets.append(sock)
    
    try:
        with pytest.raises(RuntimeError) as exc_info:
            pm.find_available_port(preferred_port=9000)
        
        # Error message should be actionable
        assert "No available ports" in str(exc_info.value)
        assert "Close some Cursor windows" in str(exc_info.value)
    finally:
        for sock in sockets:
            sock.close()

def test_write_state_creates_file_with_correct_content(tmp_path):
    """Should create state file with all required fields."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    state_file = tmp_path / ".mcp_server_state.json"
    assert state_file.exists()
    
    import json
    state = json.loads(state_file.read_text())
    
    assert state["version"] == "1.0.0"
    assert state["transport"] == "dual"
    assert state["port"] == 4242
    assert state["host"] == "127.0.0.1"
    assert state["path"] == "/mcp"
    assert state["url"] == "http://127.0.0.1:4242/mcp"
    assert "pid" in state
    assert "started_at" in state
    assert "project" in state

def test_write_state_sets_permissions(tmp_path):
    """Should set state file permissions to 0o600."""
    pm = PortManager(tmp_path)
    pm.write_state(transport="dual", port=4242)
    
    state_file = tmp_path / ".mcp_server_state.json"
    
    # Check permissions (owner read/write only)
    assert oct(state_file.stat().st_mode)[-3:] == "600"

@patch('subprocess.run')
def test_project_discovery_extracts_name_from_git(mock_run, tmp_path):
    """Should extract project name from git remote URL."""
    # Mock git command output
    mock_run.return_value = Mock(
        stdout="git@github.com:user/my-project.git\n",
        returncode=0
    )
    
    # Create fake .git directory
    (tmp_path / ".git").mkdir()
    
    from mcp_server.project_info import ProjectInfoDiscovery
    discovery = ProjectInfoDiscovery(tmp_path / ".praxis-os")
    
    info = discovery.get_project_info()
    
    assert info["name"] == "my-project"

def test_project_discovery_fallback_to_directory_name(tmp_path):
    """Should use directory name if not a git repo."""
    from mcp_server.project_info import ProjectInfoDiscovery
    
    # No .git directory
    discovery = ProjectInfoDiscovery(tmp_path / ".praxis-os")
    
    info = discovery.get_project_info()
    
    # Should use directory name as fallback
    assert info["name"] == tmp_path.name
```

### Integration Testing Approach

**Philosophy:**
- Test components working together
- Use real subprocess (not mocked)
- Test end-to-end flows
- Slower but comprehensive

**Example: Dual Transport Test**
```python
# tests/integration/test_dual_transport.py

import pytest
import subprocess
import time
import json
from pathlib import Path

@pytest.mark.integration
def test_dual_transport_serves_both(test_project_path):
    """Dual transport should serve both stdio and HTTP."""
    
    # Start server in dual mode
    env = {
        "PYTHONUNBUFFERED": "1",
        **os.environ
    }
    
    proc = subprocess.Popen(
        [
            str(test_project_path / ".praxis-os/venv/bin/python"),
            "-m", "mcp_server",
            "--transport", "dual",
            "--log-level", "INFO"
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=test_project_path,
        env=env
    )
    
    try:
        # Wait for state file
        state_file = test_project_path / ".praxis-os" / ".mcp_server_state.json"
        state = wait_for_state_file(state_file, timeout=10)
        
        assert state["transport"] == "dual"
        assert state["port"] is not None
        assert state["url"] is not None
        
        # Test HTTP endpoint
        import requests
        response = requests.post(
            state["url"],
            json={"jsonrpc": "2.0", "method": "tools/list", "id": 1},
            headers={"Accept": "application/json, text/event-stream"}
        )
        assert response.status_code == 200
        
        # Test stdio
        request = json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }) + "\n"
        
        proc.stdin.write(request.encode())
        proc.stdin.flush()
        
        line = proc.stdout.readline()
        result = json.loads(line)
        assert "result" in result
        
    finally:
        # Cleanup
        proc.terminate()
        proc.wait(timeout=5)

def wait_for_state_file(state_file: Path, timeout: int = 10) -> dict:
    """Wait for state file to appear."""
    start = time.time()
    while time.time() - start < timeout:
        if state_file.exists():
            try:
                return json.loads(state_file.read_text())
            except json.JSONDecodeError:
                time.sleep(0.5)
                continue
        time.sleep(0.5)
    
    raise TimeoutError(f"State file not created within {timeout} seconds")
```

**Example: Multi-Project Test**
```python
# tests/integration/test_multi_project.py

@pytest.mark.integration
def test_multiple_projects_no_conflicts(project_a, project_b, project_c):
    """Multiple projects should get different ports."""
    
    # Start 3 servers
    servers = []
    for project in [project_a, project_b, project_c]:
        proc = start_server(project, transport="http")
        servers.append(proc)
    
    try:
        # Read state files
        state_a = read_state(project_a / ".praxis-os")
        state_b = read_state(project_b / ".praxis-os")
        state_c = read_state(project_c / ".praxis-os")
        
        # All should have different ports
        ports = {state_a["port"], state_b["port"], state_c["port"]}
        assert len(ports) == 3, "All servers should have unique ports"
        
        # All should be accessible
        assert is_server_responding(state_a["url"])
