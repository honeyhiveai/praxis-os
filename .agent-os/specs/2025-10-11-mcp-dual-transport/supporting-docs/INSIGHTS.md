# Extracted Insights from Supporting Documents

**Date:** 2025-10-11  
**Phase:** 0 (Supporting Documents Integration)

---

## Requirements Insights (Phase 1)

### From DESIGN-DOC-MCP-Dual-Transport.md:

**User Needs:**
- **Multi-agent Access:** IDE and sub-agents (Cline, Aider, custom) need simultaneous access to same MCP server
- **Zero-conflict Multi-project:** Multiple Cursor windows open different projects without port conflicts
- **Sub-agent Discovery:** Sub-agents need automatic way to discover and connect to project's MCP server
- **Project Isolation:** Each project's MCP server must be independent (separate state, RAG, ports)

**Business Goals:**
- Enable sub-agent ecosystem around Agent OS
- Reduce friction for multi-project workflows
- Maintain backward compatibility with existing deployments
- Zero configuration required for sub-agents

**Functional Requirements:**
- FR-1: Support stdio transport for IDE communication (existing)
- FR-2: Support HTTP transport for sub-agent communication (new)
- FR-3: Support dual transport mode (stdio + HTTP simultaneously) (new)
- FR-4: Automatic port allocation in range 4242-5242 to avoid conflicts
- FR-5: State file generation at `.agent-os/.mcp_server_state.json` with HTTP URL
- FR-6: Project information discovery (name, root, git info) without hardcoding
- FR-7: Graceful shutdown with state file cleanup
- FR-8: All tools available on both transports
- FR-9: Thread-safe concurrent request handling

**Constraints:**
- Must run from `.agent-os/venv/` for dependencies (lancedb, playwright, watchdog)
- HTTP must bind to localhost only (127.0.0.1) for security
- No authentication required (localhost trust model)
- Port range limited to 4242-5242 (1000 concurrent servers max)
- State file is runtime-only, not persistent storage

**Out of Scope:**
- Remote/public HTTP access (security implications)
- Load balancing across multiple servers
- Hot reload of transport mode
- Multi-server aggregation for sub-agents
- Persistent state storage

---

## Design Insights (Phase 2)

### From DESIGN-DOC-MCP-Dual-Transport.md:

**Architecture:**
- Main thread runs stdio transport (blocking, serves IDE)
- Background daemon thread runs HTTP transport (serves sub-agents)
- Single FastMCP instance serves both transports (validated with working code)
- Dependency injection pattern for RAGEngine, WorkflowEngine, etc.
- Project isolation through independent server processes per project

**Components:**
- **PortManager** (`mcp_server/port_manager.py`): Port allocation, state file read/write, cleanup
- **ProjectInfoDiscovery** (`mcp_server/project_info.py`): Dynamic project metadata via git commands
- **Updated Entry Point** (`mcp_server/__main__.py`): CLI arg parsing, transport orchestration
- **State File** (`.agent-os/.mcp_server_state.json`): JSON with transport, port, URL, PID, timestamp

**Technology Choices:**
- Python threading for concurrent transports (proven stable)
- FastMCP framework (supports stdio and streamable-http)
- Socket binding test for port availability check
- subprocess calls for git information discovery
- JSON for state file format

**Data Models:**
```python
# State File Schema
{
  "version": "1.0.0",
  "transport": "dual" | "stdio" | "http",
  "port": int | null,
  "host": "127.0.0.1",
  "path": "/mcp",
  "url": str | null,
  "pid": int,
  "started_at": ISO8601,
  "project": {
    "name": str,  # from git or directory name
    "root": str   # filesystem path
  }
}
```

**APIs/Interfaces:**
- **CLI Interface:** `python -m mcp_server --transport {dual|stdio|http} [--log-level DEBUG]`
- **PortManager.find_available_port(preferred: int) -> int:** Tries preferred, increments if taken
- **PortManager.write_state(transport, port, host, path):** Atomic write to state file
- **PortManager.read_state(base_path) -> Optional[Dict]:** Read/validate state file
- **ProjectInfoDiscovery.get_project_info() -> Dict:** Dynamic project metadata
- **New MCP Tool:** `get_server_info() -> dict` for client verification

**Security:**
- HTTP binds to 127.0.0.1 only (never 0.0.0.0)
- State file permissions: 0o600 (owner read/write only)
- No authentication (localhost trust model)
- State file gitignored (not committed to repo)

---

## Implementation Insights (Phase 4)

### From DESIGN-DOC-MCP-Dual-Transport.md:

**Code Patterns:**
```python
# Port allocation algorithm
for port in range(preferred_port, 5242):
    try:
        with socket.socket() as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("127.0.0.1", port))
            return port
    except OSError:
        continue

# Dual transport orchestration
http_thread = threading.Thread(
    target=lambda: mcp.run(transport="streamable-http", ...),
    daemon=True
)
http_thread.start()
time.sleep(2)  # Wait for HTTP ready
mcp.run(transport="stdio")  # Blocks in main thread
```

**Testing Strategy:**
- Unit tests: Port allocation, state file management, project discovery
- Integration tests: Dual transport with both stdio and HTTP clients
- Multi-project tests: 3+ servers on different ports simultaneously
- Error scenario tests: Port exhaustion, state file corruption, crashes
- Thread safety tests: Concurrent requests from both transports

**Deployment:**
- Update `.cursor/mcp.json` with `["--transport", "dual"]` argument
- Add `.agent-os/.mcp_server_state.json` to `.gitignore`
- No breaking changes - existing `--transport stdio` still works
- State file auto-created on startup, auto-deleted on shutdown
- Sub-agents read state file for HTTP URL discovery

**Monitoring:**
- State file includes PID for health checks
- State file includes timestamp for uptime calculation
- Logging at INFO level shows transport mode, ports, URLs
- Sub-agents should validate PID before connecting (detect stale state)

**Error Handling:**
- Port allocation exhaustion: Log error, suggest closing windows, exit(1)
- State file corruption: Delete and regenerate
- HTTP startup failure: Cleanup state file, don't advertise
- Stale state file: Sub-agents check PID validity with `os.kill(pid, 0)`

---

## Cross-References

**Validated by Multiple Sources:**
- Dual transport feasibility validated with working proof-of-concept code
- FastMCP supports both stdio and HTTP transports from same instance
- Port allocation algorithm tested and proven
- MCP SDK client successfully called tools via HTTP

**Conflicts:**
- None - single authoritative design document with validation results

**High-Priority Items:**
- Port allocation must be automatic (critical for multi-project)
- State file must include HTTP URL (critical for sub-agent discovery)
- Project info must be dynamic not hardcoded (critical for portability)
- Thread safety for shared components (RAGEngine, WorkflowEngine)
- Graceful shutdown with state cleanup (critical for avoiding stale files)

---

## Insight Summary

**Total:** 45 insights  
**By Category:** Requirements [18], Design [17], Implementation [10]  
**Multi-source validated:** 4 (dual transport, port allocation, MCP SDK compatibility, project isolation)  
**Conflicts to resolve:** 0  
**High-priority items:** 5

**Phase 0 Complete:** ✅ 2025-10-11

