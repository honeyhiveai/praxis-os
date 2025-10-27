# Supporting Documents Index

**Spec**: Browser Automation Tool for Agent OS MCP Server  
**Target**: `mcp_server/browser_manager.py`  
**Created**: October 8, 2025

---

## 📚 Document Inventory

### 1. RESEARCH.md (18KB)
**Type**: Reference (too large to embed)  
**Purpose**: Comprehensive technical research on Playwright integration  
**Key Insights**:
- Playwright Python API capabilities and patterns
- Existing MCP implementations (Microsoft, others)
- BrowserManager singleton architecture
- 6 browser actions consolidated into single tool
- FastMCP integration patterns from existing codebase

**Critical Sections**:
- Component Design: BrowserManager class structure
- Browser Tools: pos_browser tool implementation
- Integration: ServerFactory modifications needed

---

### 2. SUMMARY.md (4.6KB)
**Type**: Embed  
**Purpose**: Executive summary and decision log  
**Key Insights**:
- Problem statement: Cursor's Playwright MCP is limited
- Solution: pos_browser tool with full context control
- Design decisions table (singleton, lazy init, chromium-only)
- Implementation estimate: 4-6 hours MVP
- Success criteria defined

**Critical Sections**:
- All sections - compact overview

---

### 3. TOOL_CONSOLIDATION.md (11KB)
**Type**: Reference  
**Purpose**: Analysis of granular vs consolidated tool design  
**Key Insights**:
- MCP tool limit: 20 tools (85% performance drop beyond)
- Current tool count: 8 tools
- Consolidated approach: 1 tool with actions (vs 6 granular tools)
- Saves 5 tool slots for future features
- Action-based design pattern for extensibility

**Critical Sections**:
- Comparison table (granular vs consolidated)
- Complete tool implementation example
- Final recommendation

---

### 4. SESSION_MANAGEMENT.md (11KB)
**Type**: Reference  
**Purpose**: Browser state persistence across tool calls  
**Key Insights**:
- BrowserManager singleton maintains persistent page
- Same page instance returned across multiple tool calls
- Enables multi-step workflows (navigate → dark mode → screenshot)
- No difference in session mgmt between granular vs consolidated

**Critical Sections**:
- How Session Persistence Works (diagrams)
- Lifecycle diagram
- Consolidated vs Granular comparison

---

### 5. CONCURRENCY_ANALYSIS.md (19KB)
**Type**: Reference  
**Purpose**: Multi-session safety for concurrent Cursor chats  
**Key Insights**:
- ⚠️ CRITICAL: Multiple chats share one MCP server instance
- Problem: Shared singleton = state corruption between chats
- Solution: Session-based browser contexts (isolation per chat)
- Required: `session_id` parameter for isolation
- AsyncIO locks for thread safety

**Critical Sections**:
- The Problem: Shared State Catastrophe
- Solution 1: Session-Based Browser Isolation (RECOMMENDED)
- Multi-Session BrowserManager implementation
- Thread Safety Considerations

---

### 6. NAMING_STRATEGY.md (9.9KB)
**Type**: Reference  
**Purpose**: Avoiding tool name collisions with Cursor  
**Key Insights**:
- Cursor has `mcp_cursor-playwright_*` namespaced tools
- No current collisions with our 8 existing tools
- Recommendation: `pos_` prefix for new specialized tools
- Final name: `pos_browser` (not just `browser`)
- Establishes namespace pattern for future tools

**Critical Sections**:
- Name Collision Check table
- Recommended name: `pos_browser`
- Naming consistency guidelines

---

## 🔗 Cross-References

### Architecture Dependencies
- RESEARCH.md → Defines BrowserManager class
- SESSION_MANAGEMENT.md → Explains persistence model
- CONCURRENCY_ANALYSIS.md → Adds session isolation to BrowserManager

### Design Decisions
- TOOL_CONSOLIDATION.md → Why 1 tool not 6
- NAMING_STRATEGY.md → Why `pos_browser` not `browser`
- SUMMARY.md → Records all key decisions

### Implementation Priority
1. **Phase 1**: CONCURRENCY_ANALYSIS.md (session isolation is critical)
2. **Phase 2**: RESEARCH.md (core implementation)
3. **Phase 3**: TOOL_CONSOLIDATION.md (tool structure)
4. **Phase 4**: NAMING_STRATEGY.md (final naming)

---

## 📊 Document Mode Summary

| Document | Size | Mode | Reason |
|----------|------|------|--------|
| RESEARCH.md | 18KB | Reference | Too large, technical details |
| SUMMARY.md | 4.6KB | Embed | Compact overview |
| TOOL_CONSOLIDATION.md | 11KB | Reference | Detailed analysis |
| SESSION_MANAGEMENT.md | 11KB | Reference | Technical deep-dive |
| CONCURRENCY_ANALYSIS.md | 19KB | Reference | Critical but lengthy |
| NAMING_STRATEGY.md | 9.9KB | Reference | Detailed strategy |

**Total**: ~80KB of research
**Embedded**: 4.6KB (SUMMARY.md only)
**Referenced**: 75.4KB (5 docs)

---

## ✅ Key Takeaways for Spec

1. **Tool Name**: `pos_browser` (with `pos_` namespace)
2. **Architecture**: Multi-session BrowserManager with isolated contexts
3. **Tool Structure**: Single consolidated tool with action parameter
4. **Parameters**: Requires `session_id` for concurrency safety
5. **Actions**: navigate, emulate_media, screenshot, set_viewport, close
6. **Dependencies**: playwright>=1.40.0, chromium (~300MB)
7. **Integration**: ServerFactory → BrowserManager → register browser tools
8. **Tool Count**: 9 total after adding (well under 20 limit)

---

## 🎯 Next Phase

With supporting docs processed, ready for:
- Phase 1: Requirements definition
- Phase 2: Detailed specification
- Phase 3: Task breakdown
- Phase 4: Implementation guidance
- Phase 5: Validation & testing

