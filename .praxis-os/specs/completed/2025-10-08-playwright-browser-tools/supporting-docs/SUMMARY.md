# Playwright Browser Tools - Executive Summary

**Status**: Research Complete  
**Date**: October 8, 2025  
**Next Step**: Create full spec using `spec_creation_v1` workflow

---

## 🎯 What We're Building

**Add Playwright browser automation tools to Agent OS Enhanced MCP server** to enable:
- ✅ Dark mode emulation for documentation testing
- ✅ Full browser context control (viewport, geolocation, permissions)
- ✅ Comprehensive screenshot capabilities
- ✅ Programmatic browser automation for AI agents

---

## 🔥 Why This Matters

**Current Problem**: Cursor's Playwright MCP tool is limited and cannot:
- Emulate dark mode (`page.emulateMedia({ colorScheme: 'dark' })`)
- Configure browser contexts
- Maintain persistent sessions

**Business Impact**:
- Cannot validate documentation sites properly
- Cannot test dark mode themes
- Limited browser automation for testing workflows
- Agent OS Enhanced should be self-sufficient for web testing

---

## 🏗️ Design Overview

### Architecture: 3 Components

1. **`BrowserManager`** (Singleton)
   - Manages persistent Playwright browser instance
   - Handles context/page lifecycle
   - Provides resource cleanup

2. **Browser Tools** (6 MCP Tools)
   - `browser_navigate()` - Navigate to URLs
   - `browser_emulate_media()` - ⭐ Dark mode, reduced motion
   - `browser_screenshot()` - Full-page or viewport screenshots
   - `browser_set_viewport()` - Resize browser window
   - `browser_get_console()` - Console message capture
   - `browser_close()` - Clean shutdown

3. **ServerFactory Integration**
   - Inject `BrowserManager` into server
   - Register browser tools as new tool group
   - Lazy initialization on first use

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Browser Instance | Singleton | Efficiency, state preservation |
| Initialization | Lazy (on first tool call) | Avoid blocking server startup |
| Browser Selection | Chromium only (v1) | Simplicity, most common use case |
| Tool Organization | New "browser" tool group | Selective loading, clear separation |
| Async Handling | Async/await throughout | Matches Playwright + FastMCP patterns |

---

## 📊 Implementation Estimate

**Effort**: ~4-6 hours for MVP
- Phase 1: Core `BrowserManager` - 2h
- Phase 2: Basic tools (4 tools) - 2h
- Phase 3: Integration - 1h
- Phase 4: Testing & docs - 1h

**Dependencies**:
- `playwright>=1.40.0` (~5MB)
- Chromium browser (~300MB)

**Files to Create/Modify**:
- ✨ `mcp_server/browser_manager.py` (new)
- ✨ `mcp_server/server/tools/browser_tools.py` (new)
- 🔧 `mcp_server/server/factory.py` (modify)
- 🔧 `mcp_server/server/tools/__init__.py` (modify)
- 📝 `mcp_server/README.md` (update)
- 📝 `requirements.txt` (update)

---

## ✅ Success Criteria

1. **Functional**: Can emulate dark mode and test our Docusaurus site
2. **Performant**: Browser instance persists across calls (no launch overhead)
3. **Reliable**: Proper cleanup on server shutdown
4. **Maintainable**: Follows Agent OS patterns (DI, logging, HoneyHive hooks)
5. **Documented**: Clear usage examples + API reference

---

## 🚦 Next Steps

### Immediate
1. **Create full spec** using `start_workflow('spec_creation_v1', 'mcp_server/browser_manager.py')`
2. **Review research doc** (`RESEARCH.md`) for technical details
3. **Decide on open questions** (async init, headless mode, etc.)

### Implementation Order
```
Phase 1: BrowserManager
  ├─> Phase 2: Basic Tools (navigate, emulate_media, screenshot)
      ├─> Phase 3: Integration
          └─> Phase 4: Testing & Docs
```

### Post-MVP Enhancements
- [ ] Firefox/WebKit support
- [ ] Multi-instance browser management
- [ ] Console message capture with listeners
- [ ] Network request interception
- [ ] PDF generation
- [ ] Visual regression testing
- [ ] Browser pool for parallel testing

---

## 🤔 Open Questions for Review

1. **Async initialization strategy**: Lazy init on first call? (Recommended: Yes)
2. **Headless mode**: Always headless or configurable? (Recommended: Configurable)
3. **Tool group naming**: "browser" or "automation"? (Recommended: "browser")
4. **Error handling**: Retry logic for flaky browser operations? (Recommended: Simple retry)
5. **Resource limits**: Max browser memory, timeout configs? (Recommended: Add later)

---

## 📚 Key Resources

- **Research Doc**: `RESEARCH.md` (this directory)
- **Playwright Python**: https://playwright.dev/python/
- **Agent OS Patterns**: `.praxis-os/standards/workflows/`
- **Reference Implementation**: https://github.com/microsoft/playwright-mcp

---

**Ready to proceed with spec creation!** 🚀

Use: `start_workflow('spec_creation_v1', 'mcp_server/browser_manager.py')`

