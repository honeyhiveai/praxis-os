# Browser-Based Agent IDE - Design Proposal

**Date**: 2025-10-22  
**Status**: Proposal  
**Type**: New Project

## Executive Summary

A minimal browser-based IDE that provides an agent-first development environment, complementing existing desktop IDEs (Cursor, Claude Desktop) by offering a lightweight, accessible alternative. The project leverages existing open-source components (Monaco Editor, xterm.js) and integrates with the established prAxIs OS MCP infrastructure.

## Problem Statement

prAxIs OS currently requires desktop IDE installation (Cursor, Claude Desktop), creating barriers for:
- Quick remote access scenarios
- Educational/demonstration purposes  
- Platform-constrained environments (Chromebooks, tablets)
- Users wanting to try prAxIs OS without installing desktop software

## Proposed Solution

A browser-based IDE with minimal scope: code editor, file tree, agent chat, and terminal - just enough to enable agent-assisted development without overwhelming complexity.

**Key Principle**: This is NOT a VS Code competitor. It's an **agent-first interface** that reuses proven components for basic IDE functionality.

## Success Metrics

1. **Accessibility**: Zero-install experience (open browser, start coding)
2. **Integration**: Full MCP compatibility with agent-os-rag server
3. **Usability**: Support basic file operations and agent conversations
4. **Timeline**: Deliverable MVP in 3-4 weeks part-time
5. **Maintainability**: <2500 lines of custom code (excluding libraries)

## Scope Boundaries

**In Scope:**
- File viewing/editing with Monaco Editor
- Basic file tree operations (create, delete, rename)
- Agent chat interface with MCP integration
- Integrated terminal via xterm.js
- Local file system access via FastAPI backend

**Out of Scope (v1):**
- Debugger
- Advanced refactoring tools
- Git GUI (CLI via terminal only)
- Multi-user collaboration
- Cloud file sync
- Complex plugin system
- Multiple language servers
- Build tool integration

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Browser Client (React)          │
│  ┌───────────────────────────────────┐  │
│  │ Monaco Editor (code editing)      │  │
│  │ File Tree (navigation)            │  │
│  │ Chat Interface (agent comms)      │  │
│  │ Terminal (xterm.js)               │  │
│  └────────────┬──────────────────────┘  │
└───────────────┼──────────────────────────┘
                │ WebSocket + HTTP
                ↓
┌──────────────────────────────────────────┐
│      FastAPI Backend (Python)            │
│  ┌────────────────────────────────────┐  │
│  │ File Operations API                │  │
│  │ MCP Proxy (to agent-os-rag)       │  │
│  │ WebSocket Server                   │  │
│  │ Static File Serving                │  │
│  └────────────┬───────────────────────┘  │
└───────────────┼──────────────────────────┘
                │ MCP Protocol
                ↓
┌──────────────────────────────────────────┐
│     agent-os-rag MCP Server              │
│  (Existing Infrastructure)               │
│  - search_standards()                    │
│  - start_workflow()                      │
│  - pos_browser()                         │
│  - All other MCP tools                   │
└──────────────────────────────────────────┘
```

## Technology Stack

**Frontend:**
- React 18 (UI framework)
- Monaco Editor (code editing)
- xterm.js (terminal emulation)
- react-folder-tree (file browser)
- TailwindCSS (styling)
- Native WebSocket API

**Backend:**
- FastAPI (Python web server)
- MCP Python SDK (protocol client)
- uvicorn (ASGI server)
- pathlib (file operations)

**Infrastructure:**
- Docker (containerization)
- prAxIs OS MCP server (existing)

## Implementation Phases

### Phase 1: Core Editor (Week 1)
- FastAPI server with file CRUD API
- React app with Monaco Editor
- Single file viewing/editing
- Basic styling

### Phase 2: Agent Integration (Week 2)
- Chat UI component
- WebSocket connection
- MCP proxy implementation
- Agent response display

### Phase 3: Terminal & File Tree (Week 3)
- xterm.js integration
- Shell process spawning
- File tree component
- Create/delete/rename operations

### Phase 4: Polish (Week 4)
- Split-pane layout
- Keyboard shortcuts
- Settings (theme, font size)
- Error handling
- Documentation

## Risk Assessment

**Technical Risks:**
- WebSocket connection stability → Mitigation: Auto-reconnect logic
- File system security → Mitigation: Path validation, sandboxing
- MCP protocol compatibility → Mitigation: Use official SDK

**Scope Risks:**
- Feature creep → Mitigation: Strict v1 scope adherence
- Over-engineering → Mitigation: Use existing components, minimal custom code

**Timeline Risks:**
- Underestimated complexity → Mitigation: 3-4 week buffer, phased delivery

## Open Questions

1. **Authentication**: Required for multi-user scenarios? (v2 consideration)
2. **File Sync**: Local only or support remote? (Start local, add later)
3. **Browser Support**: Target modern browsers only? (Yes, Chrome/Firefox/Safari)
4. **Deployment**: Docker container sufficient? (Yes for v1)

## Next Steps

1. **Review this proposal** for feasibility and scope accuracy
2. **Create detailed technical specs** (specs.md)
3. **Break down implementation tasks** (tasks.md)
4. **Generate implementation guide** (implementation.md)
5. **Begin Phase 1 development** when ready

## Quick Links

- **Requirements**: [srd.md](srd.md)
- **Technical Design**: [specs.md](specs.md)
- **Implementation Tasks**: [tasks.md](tasks.md)
- **Implementation Guide**: [implementation.md](implementation.md)

## Resources

**Similar Projects (Reference):**
- Monaco Editor Playground: https://microsoft.github.io/monaco-editor/
- StackBlitz (browser IDE): https://stackblitz.com/
- CodeSandbox (browser IDE): https://codesandbox.io/

**Key Libraries:**
- Monaco Editor: https://github.com/microsoft/monaco-editor
- xterm.js: https://xtermjs.org/
- FastAPI: https://fastapi.tiangolo.com/
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk

---

**For Implementers:**
1. Read [srd.md](srd.md) for requirements context
2. Review [specs.md](specs.md) for technical design
3. Follow [tasks.md](tasks.md) for implementation sequence
4. Reference [implementation.md](implementation.md) for patterns

**For Reviewers:**
- Focus on scope appropriateness (is it minimal yet viable?)
- Validate timeline estimates (3-4 weeks feasible?)
- Check technical approach (leveraging existing components?)
- Assess risk mitigation strategies
