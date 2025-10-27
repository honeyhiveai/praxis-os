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

