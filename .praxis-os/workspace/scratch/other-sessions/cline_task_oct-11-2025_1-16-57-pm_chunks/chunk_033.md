    )
    
    # Wait for state file
    state = wait_for_state_file(test_project_path / ".praxis-os")
    
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
    state_a = read_state(project_a / ".praxis-os")
    state_b = read_state(project_b / ".praxis-os")
    state_c = read_state(project_c / ".praxis-os")
    
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
4. **Filesystem Access:** Sub-agents can read .praxis-os/.mcp_server_state.json (same user)
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
| 2025-10-11 | 1.0 | Initial technical specifications | prAxIs OS Team |


</file_content>

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport/srd.md">
# Software Requirements Document

**Project:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11  
**Priority:** High  
**Category:** Feature

---

## 1. Introduction

### 1.1 Purpose

This document defines the requirements for implementing dual-transport support in the prAxIs OS MCP server, enabling simultaneous stdio (for IDEs) and HTTP (for sub-agents) communication with automatic port allocation and zero-conflict multi-project support.

### 1.2 Scope

This feature will:
- Enable a single MCP server to serve both stdio and HTTP transports simultaneously
- Automatically allocate HTTP ports to avoid conflicts when multiple projects are open
- Provide state file-based discovery mechanism for sub-agents
- Maintain complete project isolation across multiple Cursor windows
- Preserve backward compatibility with existing stdio-only deployments

### 1.3 Supporting Documentation

Requirements in this document are informed by:
- **DESIGN-DOC-MCP-Dual-Transport.md**: Complete architectural design with validation results

See `supporting-docs/INSIGHTS.md` for detailed extracted insights.

---

## 2. Business Goals

### Goal 1: Enable Sub-Agent Ecosystem

**Objective:** Allow sub-agents (Cline, Aider, custom agents) to access prAxIs OS MCP server alongside primary IDE, creating a collaborative multi-agent workflow environment.

**Success Metrics:**
- Sub-agent connection success rate: 0% → 95%+ (currently impossible)
- Time to connect sub-agent: N/A → < 5 seconds (read state file, connect)
- Developer setup steps for sub-agents: Manual config → Zero configuration

**Business Impact:**
- Enables prAxIs OS ecosystem expansion beyond IDE integration
- Reduces friction for developers using multiple AI agents
- Positions prAxIs OS as multi-agent collaboration platform

### Goal 2: Eliminate Multi-Project Port Conflicts

**Objective:** Allow developers to work on multiple projects simultaneously without MCP server port conflicts or manual configuration.

**Success Metrics:**
- Port conflict incidents: 100% → 0% (automatic allocation)
- Manual port configuration required: Always → Never
- Maximum concurrent projects: 1 → 1000 (port range 4242-5242)

**Business Impact:**
- Removes major friction point in multi-project workflows
- Improves developer experience for polyglot developers
- Reduces support burden from port conflict issues

### Goal 3: Maintain Backward Compatibility

**Objective:** Ensure existing prAxIs OS deployments continue working without changes while enabling new dual-transport capabilities.

**Success Metrics:**
- Breaking changes: 0 (stdio-only mode preserved)
- Migration effort for existing users: 0 manual steps (opt-in via CLI flag)
- Feature parity: 100% (all tools work on both transports)

**Business Impact:**
- Zero disruption to existing user base
- Smooth adoption path for new capabilities
- Maintains trust and stability

---

## 3. User Stories

### Story 1: Developer Opens Multiple Projects

**As a** software developer working on multiple projects  
**I want to** open 3+ Cursor windows with prAxIs OS enabled simultaneously  
**So that** I can work across projects without port conflicts or server crashes

**Acceptance Criteria:**
- Given 3 Cursor windows open with different projects
- When each starts its MCP server in dual mode
- Then each gets a unique HTTP port (e.g., 4242, 4243, 4244)
- And all servers run independently without conflicts
- And each project's RAG index remains isolated

**Priority:** Critical

### Story 2: Sub-Agent Discovers MCP Server

**As a** Cline agent running in a project  
**I want to** automatically discover the project's MCP server HTTP endpoint  
**So that** I can access prAxIs OS tools without manual configuration

**Acceptance Criteria:**
- Given prAxIs OS MCP server running in dual mode
- When Cline agent starts in the project
- Then Cline reads `.praxis-os/.mcp_server_state.json`
- And extracts HTTP URL (e.g., `http://127.0.0.1:4243/mcp`)
- And successfully connects and calls MCP tools
- And receives same results as IDE would get via stdio

**Priority:** Critical

### Story 3: IDE Uses stdio, Sub-Agent Uses HTTP

**As an** prAxIs OS user  
**I want** Cursor (stdio) and Cline (HTTP) to access the same MCP server simultaneously  
**So that** both agents share the same RAG index, workflow state, and tools

**Acceptance Criteria:**
- Given MCP server running in dual transport mode
- When Cursor calls `search_standards()` via stdio
- And Cline calls `search_standards()` via HTTP at the same time
- Then both receive results from the same RAG index
- And responses are identical (same tool implementation)
- And concurrent requests don't interfere with each other

**Priority:** High

### Story 4: Server Restarts with Port Reallocation

**As a** developer  
**I want** the MCP server to automatically find a new port if my preferred port is taken  
**So that** I never have to manually configure ports

**Acceptance Criteria:**
- Given port 4242 is already in use (another project)
- When MCP server starts with `--transport dual`
- Then server tries 4242, finds it taken, increments to 4243
- And successfully binds to 4243
- And writes correct port to state file
- And sub-agents discover the new port automatically

**Priority:** Critical

### Story 5: Graceful Shutdown Cleans State

**As a** developer  
**I want** the MCP server to clean up its state file on shutdown  
**So that** sub-agents don't try to connect to a dead server

**Acceptance Criteria:**
- Given MCP server running with state file present
- When server shuts down gracefully (Ctrl+C or IDE exit)
- Then `.mcp_server_state.json` is deleted
- And sub-agents detect absence and know server is offline
- And port is released for reuse

**Priority:** High

---

## 4. Functional Requirements

### FR-001: Dual Transport Mode Support

**Description:** The system shall support a "dual" transport mode that runs stdio (for IDE) in the main thread and HTTP (for sub-agents) in a background daemon thread from a single FastMCP instance.

**Priority:** Critical

**Related User Stories:** Story 1, Story 3

**Acceptance Criteria:**
- Single FastMCP server instance serves both transports
- Main thread runs `mcp.run(transport="stdio")`
- Background daemon thread runs `mcp.run(transport="streamable-http")`
- Both transports access the same tool registry
- Both transports access the same RAGEngine, WorkflowEngine, and state
- HTTP server starts within 5 seconds and is ready before stdio begins

### FR-002: Automatic Port Allocation

**Description:** The system shall automatically find and allocate an available HTTP port in the range 4242-5242 when starting in dual or HTTP-only mode.

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- Try preferred port (4242) first
- If taken, increment and retry (4243, 4244, ...)
- Continue until available port found or range exhausted (5242)
- Port allocation completes in < 1 second
- If all ports taken, log error with actionable message and exit(1)
- Use socket binding test to verify availability

### FR-003: State File Generation

**Description:** The system shall write a JSON state file at `.praxis-os/.mcp_server_state.json` containing transport mode, HTTP URL, process ID, and timestamp.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- State file created immediately after successful server startup
- Contains: version, transport, port, host, path, url, pid, started_at, project info
- File permissions set to 0o600 (owner read/write only)
- Atomic write (temp file + rename) to avoid corruption
- State file automatically deleted on graceful shutdown
- State file gitignored (not committed to repository)

### FR-004: Dynamic Project Discovery

**Description:** The system shall dynamically discover project information (name, root path, git details) without hardcoded values, using git commands and filesystem operations.

**Priority:** High

**Related User Stories:** Story 2

**Acceptance Criteria:**
- Project name derived from git repository name or directory name
- Project root determined from `.praxis-os` parent directory
- Git info obtained via subprocess calls (remote, branch, commit, status)
- Graceful fallback to directory name if not a git repository
- Discovery occurs at runtime (not build-time)
- No hardcoded paths or project names in code

### FR-005: Explicit Transport Mode CLI

**Description:** The system shall require an explicit `--transport` CLI argument specifying the transport mode: dual, stdio, or http.

**Priority:** High

**Related User Stories:** Story 1, Story 3

**Acceptance Criteria:**
- `--transport` argument is required (no default)
- Valid values: "dual", "stdio", "http"
- Invalid value logs error with usage help and exits
- Clear logging shows selected mode on startup
- Mode documented in state file
- IDE configuration specifies: `["--transport", "dual"]`

### FR-006: stdio-only Mode (Backward Compatibility)

**Description:** The system shall support `--transport stdio` mode that runs only stdio transport with no HTTP server, preserving existing behavior.

**Priority:** Critical

**Related User Stories:** Story 3 (backward compatibility aspect)

**Acceptance Criteria:**
- `--transport stdio` runs stdio transport only
- No HTTP server started
- No port allocation performed
- State file created with transport="stdio", port=null, url=null
- All existing tools and features work identically
- Zero breaking changes for existing deployments

### FR-007: HTTP-only Mode

**Description:** The system shall support `--transport http` mode that runs only HTTP transport, enabling standalone server deployment.

**Priority:** Medium

**Related User Stories:** Future: system service deployment

**Acceptance Criteria:**
- `--transport http` runs HTTP transport only in main thread
- No stdio communication
- Port allocation performed
- State file contains HTTP URL
- All tools available via HTTP
- Useful for systemd service or Docker deployment

### FR-008: Tool Parity Across Transports

**Description:** The system shall provide identical tool access and functionality on both stdio and HTTP transports.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- All registered MCP tools callable via stdio
- All registered MCP tools callable via HTTP
- Tool responses identical for same inputs
- No transport-specific tool filtering
- Error handling consistent across transports

### FR-009: Server Info Discovery Tool

**Description:** The system shall provide a `get_server_info` MCP tool that returns comprehensive server and project metadata for client verification.

**Priority:** Medium

**Related User Stories:** Story 2

**Acceptance Criteria:**
- Tool returns: server version, transport mode, uptime, PID, start time
- Tool returns: project name, root, git info (all dynamically discovered)
- Tool returns: capabilities (tool count, RAG status, features)
- Discovery happens at call time (fresh data)
- Callable via both stdio and HTTP
- Sub-agents can verify connection to correct project

### FR-010: Graceful Shutdown

**Description:** The system shall gracefully shut down both transports on termination signal (Ctrl+C, SIGTERM) and clean up state file.

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- Catches KeyboardInterrupt (Ctrl+C)
- Stops HTTP thread if running
- Deletes state file
- Closes file watchers
- Releases port
- Logs shutdown message
- Exits with code 0

### FR-011: Thread-Safe Component Access

**Description:** The system shall ensure RAGEngine, WorkflowEngine, and other shared components are thread-safe for concurrent access from stdio and HTTP transports.

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- RAGEngine query() method is thread-safe
- WorkflowEngine session access is thread-safe
- File watchers handle concurrent events
- No race conditions in state updates
- No deadlocks under concurrent load
- Validated via concurrent request testing

---

## 5. Non-Functional Requirements

### 5.1 Performance

**NFR-P1: Port Allocation Speed**
- Port allocation completes in < 1 second even when scanning range
- Minimal impact on server startup time (< 5% increase)

**NFR-P2: HTTP Server Startup**
- HTTP server ready and accepting connections within 5 seconds
- stdio begins only after HTTP health check passes

**NFR-P3: Concurrent Request Handling**
- No performance degradation with simultaneous stdio + HTTP requests
- Both transports maintain < 200ms p95 response time for typical queries

### 5.2 Security

**NFR-S1: Localhost-Only Binding**
- HTTP server MUST bind to 127.0.0.1 only (never 0.0.0.0)
- No network exposure to external interfaces
- Enforced in code with validation

**NFR-S2: State File Permissions**
- State file created with 0o600 permissions (owner read/write only)
- Prevents other users from reading HTTP URL and port

**NFR-S3: No Authentication Required**
- No authentication for localhost HTTP (same trust model as stdio)
- Acceptable because binding is localhost-only

### 5.3 Reliability

**NFR-R1: Automatic Conflict Resolution**
- 100% success rate for port allocation (within range)
- Zero manual intervention required for multi-project scenarios

**NFR-R2: State File Integrity**
- Atomic writes prevent corruption
- State file always valid JSON or absent
- Sub-agents validate PID before connecting (detect stale state)

**NFR-R3: Graceful Degradation**
- If HTTP startup fails, log error and exit (don't run stdio with broken HTTP)
- Clear error messages with remediation steps

### 5.4 Scalability

**NFR-SC1: Multi-Project Support**
- Support up to 1000 concurrent projects (port range 4242-5242)
- Each project's server independent (no shared state)
- Port reuse after shutdown

### 5.5 Usability

**NFR-U1: Zero-Configuration Sub-Agents**
- Sub-agents need only read state file to discover server
- No manual URL/port configuration required
- Clear documentation for sub-agent integration

**NFR-U2: Clear Error Messages**
- Port exhaustion: "No available ports in range 4242-5242. Close some Cursor windows and retry."
- State file corruption: Instructions to restart server
- HTTP startup failure: Suggest firewall/permissions check

### 5.6 Maintainability

**NFR-M1: Code Organization**
- Clear separation: PortManager, ProjectInfoDiscovery, entry point
- Dependency injection for testability
- Comprehensive docstrings and type hints

**NFR-M2: Test Coverage**
- Unit tests: Port allocation, state file management, project discovery
- Integration tests: Dual transport, multi-project scenarios
- Minimum 80% code coverage for new components

---

## 6. Out of Scope

### Explicitly Excluded

#### Features

**Not Included in This Release:**

1. **Remote/Public HTTP Access**
   - **Reason:** Security implications require authentication, TLS, rate limiting
   - **Future Consideration:** Phase 2 with proper security layer

2. **Load Balancing Across Multiple Servers**
   - **Reason:** Single server per project is sufficient for prAxIs OS use case
   - **Future Consideration:** Enterprise deployment scenario

3. **Hot Reload of Transport Mode**
   - **Reason:** Requires complex state synchronization, low value
   - **Future Consideration:** Unlikely to be needed

4. **Multi-Server Aggregation for Sub-Agents**
   - **Reason:** Sub-agents typically work within one project at a time
   - **Future Consideration:** Advanced orchestration scenarios

5. **Persistent State Storage**
   - **Reason:** State file is runtime-only for discovery, not data persistence
   - **Future Consideration:** Not needed for current architecture

6. **Custom Port Range Configuration**
   - **Reason:** Fixed range 4242-5242 sufficient for vast majority of users
   - **Future Consideration:** Config file option if user feedback requests

#### Platforms / Environments

**Not Supported:**
- **Windows:** No specific Windows testing (should work but not validated)
- **Docker/Container Deployment:** Works but not explicitly documented yet

---

## 6.1 Future Enhancements

**Potential Phase 2:**
- Health check endpoint for monitoring
- Automatic reconnection support for sub-agents
- Metrics collection (port usage, request counts)
- Remote access with authentication (optional for advanced users)

**Potential Phase 3:**
- Multi-server aggregation client
- Port range configuration via config file
- WebSocket transport alternative to HTTP
- Browser-based sub-agent dashboard

---

## 7. Success Criteria

This feature will be considered successful when:

✅ Multiple Cursor windows can open with prAxIs OS without conflicts  
✅ Sub-agents discover and connect to MCP server with zero configuration  
✅ All existing tools work identically on both stdio and HTTP transports  
✅ State file accurately reflects server status and enables discovery  
✅ Graceful shutdown cleans up state file reliably  
✅ Zero breaking changes for existing stdio-only users  
✅ Test coverage ≥ 80% for all new components  
✅ Documentation updated with dual-transport setup instructions  
✅ At least one sub-agent example (Cline or custom) demonstrated

---

## 8. Assumptions and Dependencies

### Assumptions
- IDEs support stdio transport for MCP (Cursor, Windsurf, Claude Desktop confirmed)
- FastMCP framework supports concurrent stdio + HTTP from same instance (validated with working code)
- Sub-agents can read JSON files from filesystem
- Port range 4242-5242 is not blocked by firewalls
- Python threading is sufficient for concurrent transport handling

### Dependencies
- FastMCP library (existing dependency)
- MCP SDK for testing HTTP transport
- Python 3.8+ threading support
- Unix/Linux socket operations (tested on macOS)

---

## 9. Revision History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-10-11 | 1.0 | Initial requirements document | prAxIs OS Team |


</file_content>

<file_content path=".praxis-os/specs/2025-10-11-mcp-dual-transport/tasks.md">
# Implementation Tasks

**Project:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11  
**Status:** Draft - Pending Approval

---

## Time Estimates

- **Phase 1:** 8-10 hours (Core Components Implementation)
- **Phase 2:** 6-8 hours (Integration & Testing)
- **Phase 3:** 4-6 hours (Sub-Agent Support & Documentation)
- **Phase 4:** 2-3 hours (Rollout & Monitoring)
- **Total:** 20-27 hours (2.5-3.5 days)

---

## Phase 1: Core Components Implementation

**Objective:** Implement PortManager, ProjectInfoDiscovery, TransportManager, and update entry point with dual-transport support.

**Estimated Duration:** 8-10 hours

### Phase 1 Tasks

- [ ] **Task 1.1**: Implement PortManager
  - Create `mcp_server/port_manager.py`
  - Implement `find_available_port()` with range 4242-5242
  - Implement `write_state()` with atomic write (temp + rename)
  - Implement `read_state()` class method
  - Implement `cleanup_state()` for shutdown
  - Implement `_is_port_available()` using socket binding test
  - Add comprehensive docstrings and type hints
  - Verify port allocation algorithm with manual testing
  
  **Acceptance Criteria:**
  - [ ] `find_available_port()` tries preferred port first (4242)
  - [ ] Port allocation increments if port taken (4243, 4244, ...)
  - [ ] RuntimeError raised if range exhausted (4242-5242)
  - [ ] State file written with all required fields (version, transport, port, url, pid, started_at, project)
  - [ ] State file created with 0o600 permissions (owner read/write only)
  - [ ] Atomic write prevents corruption (temp file + rename)
  - [ ] `read_state()` returns None for missing/corrupted files
  - [ ] `cleanup_state()` deletes state file successfully
  - [ ] All methods have docstrings and type hints

- [ ] **Task 1.2**: Implement ProjectInfoDiscovery
  - Create `mcp_server/project_info.py`
  - Implement `get_project_info()` returning name, root, praxis_os_path, git
  - Implement `_get_project_name()` with git repo name or directory fallback
  - Implement `_get_git_info()` returning remote, branch, commit, commit_short, status
  - Implement `_is_git_repo()` checking for .git directory
  - Implement `_run_git_command()` with subprocess, timeout, error handling
  - Implement individual git command methods (_get_git_remote, _get_git_branch, etc.)
  - Verify discovery works for both git and non-git projects
  
  **Acceptance Criteria:**
  - [ ] Project name extracted from git remote URL (e.g., "praxis-os" from git@github.com:user/praxis-os.git)
  - [ ] Falls back to directory name if not a git repo
  - [ ] Git info returned with remote, branch, commit, commit_short, status
  - [ ] Returns None for git info if not a git repo (graceful fallback)
  - [ ] Git commands timeout after 5 seconds
  - [ ] Git command failures handled gracefully (return None)
  - [ ] No hardcoded project names or paths in code
  - [ ] All methods have docstrings and type hints

- [ ] **Task 1.3**: Implement TransportManager
  - Create `mcp_server/transport_manager.py`
  - Implement `__init__()` accepting FastMCP instance and config
  - Implement `run_dual_mode()` orchestrating stdio (main) + HTTP (background)
  - Implement `run_stdio_mode()` for stdio-only
  - Implement `run_http_mode()` for HTTP-only
  - Implement `_start_http_thread()` creating daemon thread
  - Implement `_wait_for_http_ready()` with socket connection polling
  - Implement `shutdown()` for graceful cleanup
  - Verify HTTP server starts and is ready before stdio begins
  
  **Acceptance Criteria:**
  - [ ] `run_dual_mode()` starts HTTP in daemon thread
  - [ ] HTTP readiness check succeeds within 5 seconds
  - [ ] RuntimeError raised if HTTP fails to start
  - [ ] stdio runs in main thread (blocking)
  - [ ] `run_stdio_mode()` runs stdio-only without HTTP
  - [ ] `run_http_mode()` runs HTTP-only in main thread
  - [ ] Daemon thread behavior (dies with main thread)
  - [ ] Clear logging at INFO level for startup events
  - [ ] All methods have docstrings and type hints

- [ ] **Task 1.4**: Update Entry Point (__main__.py)
  - Add CLI argument parser with `--transport` (required) and `--log-level` (optional)
  - Validate `--transport` choices: dual, stdio, http
  - Initialize PortManager with base_path
  - Initialize TransportManager with MCP instance and config
  - Implement dual mode execution path
  - Implement stdio mode execution path
  - Implement HTTP mode execution path
  - Add try/except/finally block for graceful shutdown
  - Call `port_manager.cleanup_state()` in finally block
  - Call `transport_mgr.shutdown()` in finally block
  - Add logging for startup, shutdown, errors
  
  **Acceptance Criteria:**
  - [ ] `--transport` argument is required (error if missing)
  - [ ] Invalid transport value shows error and usage help
  - [ ] `--log-level` optional with default INFO
  - [ ] Dual mode finds port, writes state, runs dual transport
  - [ ] stdio mode writes state with port=null, runs stdio-only
  - [ ] HTTP mode finds port, writes state, runs HTTP-only
  - [ ] KeyboardInterrupt (Ctrl+C) handled gracefully
  - [ ] State file cleaned up in finally block
  - [ ] Clear error messages with remediation steps
  - [ ] Logging shows transport mode, port, URL on startup

- [ ] **Task 1.5**: Update Configuration Schema
  - Add `http_port`, `http_host`, `http_path` to MCPConfig in `mcp_server/models/config.py`
  - Set default values: http_port=4242, http_host="127.0.0.1", http_path="/mcp"
  - Update config validator to validate new fields
  - Update `.praxis-os/config.yaml` template with new fields
  - Verify config loading includes HTTP settings
  
  **Acceptance Criteria:**
  - [ ] MCPConfig dataclass includes http_port, http_host, http_path fields
  - [ ] Default values set correctly
  - [ ] Config validator checks http_port is 1024-65535
  - [ ] Config validator checks http_host is "127.0.0.1" (enforced)
  - [ ] Config validator checks http_path starts with "/"
  - [ ] Existing config files load without errors (backward compatible)
  - [ ] New config fields documented in template

- [ ] **Task 1.6**: Add get_server_info MCP Tool
  - Create new tool in `mcp_server/server/tools/server_info_tools.py`
  - Implement `register_server_info_tools()` function
  - Implement `get_server_info()` tool returning server, project, capabilities
  - Pass ProjectInfoDiscovery instance via dependency injection
  - Call `project_discovery.get_project_info()` dynamically
  - Include runtime data: uptime, PID, tool count, transport mode
  - Verify tool callable via both stdio and HTTP
  
  **Acceptance Criteria:**
  - [ ] Tool registered with FastMCP
  - [ ] Returns server metadata (version, transport, uptime, pid, started_at)
  - [ ] Returns project metadata (name, root, praxis_os_path, git)
  - [ ] Returns capabilities (tools_available, rag_enabled, etc.)
  - [ ] All values discovered at runtime (no hardcoding)
  - [ ] Tool has comprehensive docstring with example
  - [ ] Callable via both stdio and HTTP transports
  - [ ] Response follows documented schema

- [ ] **Task 1.7**: Update .gitignore
  - Add `.praxis-os/.mcp_server_state.json` to `.gitignore`
  - Verify state file not tracked by git
  
  **Acceptance Criteria:**
  - [ ] State file pattern added to .gitignore
  - [ ] Git status doesn't show state file as untracked
  - [ ] State file properly ignored across projects

---

## Phase 2: Integration & Testing

**Objective:** Validate dual-transport functionality, test multi-project scenarios, ensure thread safety, and verify error handling.

**Estimated Duration:** 6-8 hours

### Phase 2 Tasks

- [ ] **Task 2.1**: Write Unit Tests for PortManager
  - Create `tests/unit/test_port_manager.py`
  - Test `find_available_port()` prefers first port if available
  - Test `find_available_port()` increments if port taken
  - Test `find_available_port()` raises RuntimeError if range exhausted
  - Test `write_state()` creates file with correct content
  - Test `write_state()` uses atomic write (temp + rename)
  - Test `write_state()` sets permissions to 0o600
  - Test `read_state()` returns dict for valid file
  - Test `read_state()` returns None for missing file
  - Test `read_state()` returns None for corrupted JSON
  - Test `cleanup_state()` deletes state file
  - Verify 80%+ code coverage for PortManager
  
  **Acceptance Criteria:**
  - [ ] All port allocation tests pass
  - [ ] All state file tests pass
  - [ ] Mock socket binding for port tests
  - [ ] Use pytest fixtures for tmp_path
  - [ ] Code coverage ≥ 80% for PortManager
  - [ ] Tests run in < 5 seconds
  - [ ] Clear test names and docstrings

- [ ] **Task 2.2**: Write Unit Tests for ProjectInfoDiscovery
  - Create `tests/unit/test_project_info.py`
  - Test `get_project_info()` returns complete dict
  - Test `_get_project_name()` extracts from git remote
  - Test `_get_project_name()` falls back to directory name
  - Test `_get_git_info()` returns complete git metadata
  - Test `_get_git_info()` returns None if not git repo
  - Test `_run_git_command()` handles subprocess errors
  - Test `_run_git_command()` respects timeout
  - Mock subprocess calls for git commands
  - Verify 80%+ code coverage
  
  **Acceptance Criteria:**
  - [ ] All project name tests pass
  - [ ] All git info tests pass
  - [ ] Mock subprocess.run for all tests
  - [ ] Test both success and failure paths
  - [ ] Code coverage ≥ 80% for ProjectInfoDiscovery
  - [ ] Tests run in < 5 seconds
  - [ ] Clear test names and docstrings

- [ ] **Task 2.3**: Write Unit Tests for TransportManager
  - Create `tests/unit/test_transport_manager.py`
  - Test `_start_http_thread()` creates daemon thread
  - Test `_wait_for_http_ready()` polls socket connection
  - Test `_wait_for_http_ready()` returns False on timeout
  - Mock FastMCP instance for tests
  - Verify 80%+ code coverage
  
  **Acceptance Criteria:**
  - [ ] HTTP thread creation test passes
  - [ ] HTTP readiness test passes
  - [ ] Timeout test passes
  - [ ] Mock FastMCP.run() method
  - [ ] Code coverage ≥ 80% for TransportManager
  - [ ] Tests run in < 5 seconds

- [ ] **Task 2.4**: Write Integration Tests for Dual Transport
  - Create `tests/integration/test_dual_transport.py`
  - Test server starts in dual mode successfully
  - Test state file created with correct content
  - Test HTTP endpoint responds to MCP requests
  - Test stdio interface responds to MCP requests
  - Test both transports access same tools
  - Test concurrent requests from stdio and HTTP
