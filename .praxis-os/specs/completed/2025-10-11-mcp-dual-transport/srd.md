# Software Requirements Document

**Project:** MCP Server Dual-Transport Architecture  
**Date:** 2025-10-11  
**Priority:** High  
**Category:** Feature

---

## 1. Introduction

### 1.1 Purpose

This document defines the requirements for implementing dual-transport support in the Agent OS MCP server, enabling simultaneous stdio (for IDEs) and HTTP (for sub-agents) communication with automatic port allocation and zero-conflict multi-project support.

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

**Objective:** Allow sub-agents (Cline, Aider, custom agents) to access Agent OS MCP server alongside primary IDE, creating a collaborative multi-agent workflow environment.

**Success Metrics:**
- Sub-agent connection success rate: 0% → 95%+ (currently impossible)
- Time to connect sub-agent: N/A → < 5 seconds (read state file, connect)
- Developer setup steps for sub-agents: Manual config → Zero configuration

**Business Impact:**
- Enables Agent OS ecosystem expansion beyond IDE integration
- Reduces friction for developers using multiple AI agents
- Positions Agent OS as multi-agent collaboration platform

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

**Objective:** Ensure existing Agent OS deployments continue working without changes while enabling new dual-transport capabilities.

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
**I want to** open 3+ Cursor windows with Agent OS enabled simultaneously  
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
**So that** I can access Agent OS tools without manual configuration

**Acceptance Criteria:**
- Given Agent OS MCP server running in dual mode
- When Cline agent starts in the project
- Then Cline reads `.praxis-os/.mcp_server_state.json`
- And extracts HTTP URL (e.g., `http://127.0.0.1:4243/mcp`)
- And successfully connects and calls MCP tools
- And receives same results as IDE would get via stdio

**Priority:** Critical

### Story 3: IDE Uses stdio, Sub-Agent Uses HTTP

**As an** Agent OS user  
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
   - **Reason:** Single server per project is sufficient for Agent OS use case
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
| 2025-10-11 | 1.0 | Initial requirements document | Agent OS Team |

