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
