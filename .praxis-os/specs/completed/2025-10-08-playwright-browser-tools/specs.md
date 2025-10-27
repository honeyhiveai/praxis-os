# Technical Specifications
# Browser Automation Tool for prAxIs OS MCP Server

**Version**: 1.0  
**Date**: October 8, 2025  
**Requirements**: See `srd.md`  
**Phase**: 2 of 6 (spec_creation_v1)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────┐
│ Cursor IDE (Multiple Chat Sessions)                     │
│  ├─> Chat A (Testing docs)                              │
│  ├─> Chat B (Testing login)                             │
│  └─> Chat C (Screenshots)                               │
└─────────────────┬───────────────────────────────────────┘
                  │ stdio transport
                  ↓
┌─────────────────────────────────────────────────────────┐
│ prAxIs OS MCP Server (Long-Running Process)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ServerFactory (DI Container)                      │  │
│  │  ├─> RAGEngine                                    │  │
│  │  ├─> WorkflowEngine                               │  │
│  │  └─> BrowserManager ⭐ NEW                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ MCP Tools                                         │  │
│  │  ├─> search_standards()                           │  │
│  │  ├─> start_workflow()                             │  │
│  │  └─> pos_browser() ⭐ NEW                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│ BrowserManager (Per-Session Architecture)                │
│  ├─> _sessions: Dict[session_id, BrowserSession]        │
│  └─> _lock: asyncio.Lock (dict protection only)         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────────┐
│ BrowserSession (Fully Isolated Per Chat)                 │
│  ├─> playwright: Playwright instance (per session)      │
│  ├─> browser: Chromium process (per session) ⭐         │
│  ├─> page: Page (persistent across tool calls)          │
│  ├─> created_at: timestamp                              │
│  └─> last_access: timestamp (for cleanup)               │
└─────────────────────────────────────────────────────────┘

**Comprehensive Action Support**: 30+ actions across 6 categories
- Navigation, Inspection, Interaction, Waiting, Context, Session
```

**Key Design Decisions**:
- **Per-Session Browsers**: Each session gets own browser process (FR-1, NFR-5)
- **Full Isolation**: No shared browser state (failure isolation)
- **Comprehensive Actions**: 30+ actions supporting full Playwright capabilities
- **Lazy Initialization**: Browser launches per session on first call (NFR-1)
- **AI Agent First**: Optimized for AI debugging workflows, not abstract efficiency

**Architecture: Per-Session Browsers (Fully Isolated)**

**Decision**: Each session gets its own Playwright + Chromium process

**Rationale** (AI Agent Experience > Memory Efficiency):
- ✅ **Failure isolation**: Browser crash in Chat A doesn't kill Chat B/C
- ✅ **Simpler mental model**: "My chat = My browser" (clear ownership)
- ✅ **Debugging clarity**: No "which session broke it?" confusion
- ✅ **True parallelism**: No lock contention on browser state
- ✅ **Dev machine reality**: 300MB for 3 sessions = 1.8% of 16GB RAM
- ✅ **Simpler code**: No shared browser management complexity

**Implementation**:
```python
class BrowserSession:
    playwright: Playwright  # Per session
    browser: Browser        # Per session (isolated)
    page: Page
    created_at: float
    last_access: float

class BrowserManager:
    _sessions: Dict[str, BrowserSession]  # No shared browser!
    _lock: asyncio.Lock  # Only protects dict, not browser
```

**Comprehensive Scope**: Full Playwright capabilities, phased implementation
- **Phase 1**: Core automation (click, type, fill, wait, assert)
- **Phase 2**: Advanced features (test execution ⭐, network, tabs, files)
- **Phase 3**: Power features (video, trace, performance)

**Traceability**: FR-1, FR-2, NFR-1, NFR-4, NFR-5, All 28 FRs

---

## 2. Component Specifications

### 2.1 BrowserManager

**File**: `mcp_server/browser_manager.py`

**Purpose**: Manage Playwright browser lifecycle and session isolation

**Responsibilities**:
- Initialize Playwright and browser (lazy)
- Manage session-to-context mapping
- Provide thread-safe session access
- Auto-cleanup stale sessions
- Handle graceful shutdown

**Class Specification**:

```python
from dataclasses import dataclass, field
from typing import Dict, Optional
from pathlib import Path
import asyncio
import time
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

@dataclass
class BrowserSession:
    """
    Isolated browser session for a single chat/workflow.
    
    Each session maintains its own browser context and page,
    providing isolation from other concurrent sessions.
    
    :param context: Isolated Playwright browser context
    :param page: Persistent page within the context
    :param created_at: Session creation timestamp
    :param last_access: Last activity timestamp (for cleanup)
    """
    context: BrowserContext
    page: Page
    created_at: float
    last_access: float = field(default_factory=time.time)
    
    async def cleanup(self) -> None:
        """Clean up session resources."""
        await self.page.close()
        await self.context.close()


class BrowserManager:
    """
    Singleton manager for Playwright browser with multi-session support.
    
    Manages a single browser process with multiple isolated contexts,
    one per session. Provides thread-safe access and automatic cleanup.
    
    :param session_timeout: Idle timeout in seconds (default: 3600)
    
    Concurrency:
        - Thread-safe via AsyncIO locks
        - Multiple sessions operate independently
        - Shared browser process for efficiency
    
    Lifecycle:
        - Lazy initialization on first use
        - Sessions auto-cleanup after timeout
        - Explicit cleanup via pos_browser(action="close")
    
    Example:
        >>> manager = BrowserManager()
        >>> session = await manager.get_session("chat-123")
        >>> await session.page.goto("https://example.com")
        >>> await manager.close_session("chat-123")
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize browser manager.
        
        :param session_timeout: Session idle timeout (seconds)
        """
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._session_timeout = session_timeout
    
    async def initialize(self) -> None:
        """
        Initialize Playwright and launch browser (lazy).
        
        Idempotent - safe to call multiple times.
        
        :raises RuntimeError: If browser launch fails
        """
        ...
    
    async def get_session(self, session_id: str = "default") -> BrowserSession:
        """
        Get or create isolated browser session.
        
        Thread-safe. Creates new session if doesn't exist.
        Updates last_access timestamp on existing sessions.
        
        :param session_id: Unique session identifier
        :return: Browser session for this ID
        :raises RuntimeError: If session creation fails
        """
        ...
    
    async def close_session(self, session_id: str) -> None:
        """
        Explicitly close a session and release resources.
        
        :param session_id: Session to close
        """
        ...
    
    async def _cleanup_stale_sessions(self) -> None:
        """
        Auto-cleanup sessions idle beyond timeout.
        
        Called automatically by get_session().
        Removes sessions where (now - last_access) > timeout.
        """
        ...
    
    async def shutdown(self) -> None:
        """
        Shutdown all sessions and browser process.
        
        Cleans up all resources. Call on MCP server shutdown.
        """
        ...
```

**Concurrency Analysis** (NFR-4):
- **Shared State**: `_sessions` dict (read/write by multiple async tasks)
- **Protection**: `asyncio.Lock` guards all dict operations
- **Isolation**: Browser contexts are isolated by Playwright design
- **Tested**: See `tests/unit/test_browser_manager.py`

**Traceability**: FR-1, FR-2, FR-3, NFR-1, NFR-2, NFR-3, NFR-4, NFR-5

---

### 2.2 Browser Tools

**File**: `mcp_server/server/tools/browser_tools.py`

**Purpose**: MCP tool registration for browser automation

**Responsibilities**:
- Register `pos_browser()` tool with FastMCP
- Dispatch actions to appropriate handlers
- Validate parameters
- Return structured responses
- Handle errors gracefully

**Tool Specification**:

```python
def register_browser_tools(mcp: Any, browser_manager: BrowserManager) -> int:
    """
    Register browser automation tools with MCP server.
    
    :param mcp: FastMCP server instance
    :param browser_manager: BrowserManager singleton
    :return: Number of tools registered (1)
    """
    
    @mcp.tool()
    async def pos_browser(
        action: str,
        session_id: Optional[str] = None,
        # Navigation
        url: Optional[str] = None,
        wait_until: str = "load",
        timeout: int = 30000,
        # Media emulation
        color_scheme: Optional[str] = None,
        reduced_motion: Optional[str] = None,
        # Screenshot
        screenshot_full_page: bool = False,
        screenshot_path: Optional[str] = None,
        screenshot_format: str = "png",
        # Viewport
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Browser automation tool with session isolation.
        
        Provides browser control with persistent sessions across calls.
        Each session ID gets isolated browser context for multi-chat safety.
        
        Actions:
            navigate: Navigate to URL
            emulate_media: Set color scheme (dark mode) and media features
            screenshot: Capture page screenshot (full-page or viewport)
            set_viewport: Resize browser viewport
            get_console: Get console messages (future)
            close: Close session and release resources
        
        Args:
            action: Action to perform (required)
            session_id: Session identifier for isolation (default: "default")
            url: Target URL (for navigate)
            wait_until: Wait condition (load/domcontentloaded/networkidle)
            timeout: Navigation timeout in milliseconds
            color_scheme: Color scheme (light/dark/no-preference)
            reduced_motion: Reduced motion (reduce/no-preference)
            screenshot_full_page: Capture full scrollable page
            screenshot_path: File path to save screenshot
            screenshot_format: Image format (png/jpeg)
            viewport_width: Viewport width in pixels
            viewport_height: Viewport height in pixels
        
        Returns:
            Action-specific result dictionary with status, session_id, and data
        
        Examples:
            >>> # Test dark mode
            >>> pos_browser(action="navigate", url="http://localhost:3000", session_id="test-1")
            >>> pos_browser(action="emulate_media", color_scheme="dark", session_id="test-1")
            >>> pos_browser(action="screenshot", screenshot_path="/tmp/dark.png", session_id="test-1")
            >>> pos_browser(action="close", session_id="test-1")
        
        Raises:
            ValueError: If required parameters missing for action
            RuntimeError: If browser operation fails
        """
        try:
            sid = session_id or "default"
            session = await browser_manager.get_session(sid)
            page = session.page
            
            if action == "navigate":
                # FR-4: Page Navigation
                ...
            elif action == "emulate_media":
                # FR-5: Media Emulation
                ...
            elif action == "screenshot":
                # FR-6: Screenshot Capture
                ...
            elif action == "set_viewport":
                # FR-7: Viewport Control
                ...
            elif action == "get_console":
                # FR-8: Console Messages (stub)
                ...
            elif action == "close":
                # FR-3: Resource Cleanup
                ...
            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}",
                    "valid_actions": ["navigate", "emulate_media", "screenshot", "set_viewport", "get_console", "close"]
                }
        except Exception as e:
            logger.error(f"pos_browser action '{action}' failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "action": action,
                "session_id": sid
            }
    
    return 1
```

**Traceability**: FR-4 through FR-10, NFR-6, NFR-7

---

## 3. Data Models

### 3.1 BrowserSession

**Purpose**: Encapsulate isolated browser session state

**Fields**:
- `context: BrowserContext` - Playwright context (cookies, storage isolated)
- `page: Page` - Persistent page within context
- `created_at: float` - Unix timestamp of creation
- `last_access: float` - Unix timestamp of last activity

**Lifecycle**:
1. Created by `BrowserManager.get_session()`
2. Reused across multiple `pos_browser()` calls
3. Cleaned up after timeout or explicit close

**Traceability**: FR-2, NFR-3

### 3.2 Tool Response Format

**Success Response**:
```json
{
  "status": "success",
  "session_id": "chat-123",
  "action": "navigate",
  "url": "https://example.com",
  "title": "Example Page"
}
```

**Error Response** (NFR-7):
```json
{
  "status": "error",
  "error": "Navigation timeout",
  "action": "navigate",
  "session_id": "chat-123",
  "remediation": "Increase timeout parameter or check network connectivity"
}
```

---

## 4. Interface Specifications

### 4.1 ServerFactory Integration

**File**: `mcp_server/server/factory.py`

**Modification**: Add BrowserManager to DI container

```python
class ServerFactory:
    def create_server(self) -> FastMCP:
        # ... existing components ...
        
        # Create browser manager
        browser_manager = self._create_browser_manager()
        
        # Create MCP server
        mcp = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            browser_manager=browser_manager  # ⭐ NEW
        )
        
        return mcp
    
    def _create_browser_manager(self) -> BrowserManager:
        """Create browser manager for Playwright automation."""
        logger.info("Creating browser manager...")
        return BrowserManager(session_timeout=3600)
```

**Traceability**: FR-11

### 4.2 Tool Registration

**File**: `mcp_server/server/tools/__init__.py`

**Modification**: Register browser tools conditionally

```python
def register_all_tools(
    mcp: Any,
    rag_engine: Any,
    workflow_engine: Any,
    framework_generator: Any,
    browser_manager: Optional[Any] = None,  # ⭐ NEW
    base_path: Optional[Any] = None,
    enabled_groups: Optional[List[str]] = None,
    max_tools_warning: int = 20,
) -> int:
    if enabled_groups is None:
        enabled_groups = ["rag", "workflow", "browser"]  # ⭐ ADD browser
    
    tool_count = 0
    
    # ... existing tool registration ...
    
    if "browser" in enabled_groups and browser_manager:
        from .browser_tools import register_browser_tools
        count = register_browser_tools(mcp, browser_manager)
        tool_count += count
        logger.info(f"✅ Registered {count} browser tool(s)")
    
    return tool_count
```

**Traceability**: FR-11, FR-12

---

## 5. Security Considerations

### 5.1 URL Validation
- **Risk**: SSRF (Server-Side Request Forgery)
- **Mitigation**: Browser runs headless with no external network access to host
- **Accept Risk**: Users control URLs via tool calls (intended behavior)

### 5.2 File System Access
- **Risk**: Screenshot paths could write to arbitrary locations
- **Mitigation**: Validate screenshot_path is within workspace or /tmp
- **Implementation**: Path validation in screenshot action handler

### 5.3 Resource Exhaustion
- **Risk**: Unlimited sessions could exhaust memory
- **Mitigation**: Auto-cleanup stale sessions (1hr timeout)
- **Monitoring**: Log active session count

**Traceability**: NFR-3, NFR-6

---

## 6. Performance Considerations

### 6.1 Cold Start (First Call)
- **Metric**: <2s for Playwright + Chromium launch
- **Strategy**: Lazy initialization (doesn't block server startup)
- **Traceability**: NFR-1

### 6.2 Warm Path (Subsequent Calls)
- **Metric**: <100ms per tool call (page operations only)
- **Strategy**: Reuse existing browser, context, page
- **Traceability**: NFR-2

### 6.3 Memory Footprint
- **Per Session**: ~50-100MB (browser context + page)
- **Max Sessions**: Limited by auto-cleanup (1hr timeout)
- **Monitoring**: Track `len(browser_manager._sessions)`
- **Traceability**: NFR-3

---

## 7. Error Handling

### 7.1 Browser Launch Failure
```python
try:
    browser = await playwright.chromium.launch()
except Exception as e:
    return {
        "status": "error",
        "error": f"Browser launch failed: {e}",
        "remediation": "Ensure Playwright installed: playwright install chromium"
    }
```

### 7.2 Navigation Timeout
```python
try:
    await page.goto(url, timeout=timeout)
except TimeoutError:
    return {
        "status": "error",
        "error": f"Navigation timeout ({timeout}ms)",
        "remediation": "Increase timeout parameter or check network"
    }
```

### 7.3 Session Not Found (Future)
- Currently: Auto-create on get_session()
- Future: Could add strict mode that errors on missing session

**Traceability**: NFR-6, NFR-7

---

## 8. Dependencies

### 8.1 New Dependencies

**requirements.txt**:
```txt
playwright>=1.40.0  # Browser automation
```

**Installation**:
```bash
pip install playwright
playwright install chromium  # Downloads ~300MB
```

**Traceability**: NFR-10

### 8.2 Internal Dependencies

- `mcp_server/server/factory.py` (ServerFactory)
- `mcp_server/server/tools/__init__.py` (tool registration)
- FastMCP library (existing)
- asyncio (Python stdlib)

---

## 9. Configuration

### 9.1 MCP Server Config

**File**: `.praxis-os/config.json` (or default)

```json
{
  "mcp": {
    "enabled_tool_groups": ["rag", "workflow", "browser"],
    "max_tools_warning": 20
  },
  "browser": {
    "session_timeout": 3600,
    "headless": true,
    "chromium_only": true
  }
}
```

### 9.2 Auto-Approve List

**File**: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "agent-os-rag": {
      "autoApprove": [
        "search_standards",
        "get_current_phase",
        "pos_browser"
      ]
    }
  }
}
```

**Traceability**: FR-12

---

## 10. Testing Strategy

### 10.1 Unit Tests

**File**: `tests/unit/test_browser_manager.py`

**Coverage**:
- BrowserManager initialization (lazy)
- Session creation and isolation
- Stale session cleanup
- AsyncIO lock safety
- Graceful shutdown

### 10.2 Integration Tests

**File**: `tests/integration/test_browser_tools.py`

**Coverage**:
- Full workflow: navigate → emulate → screenshot
- Multi-session isolation (parallel)
- Tool registration with ServerFactory
- Error handling (timeouts, invalid URLs)

**Traceability**: NFR-9

---

## 11. Deployment

### 11.1 Installation Steps

1. **Add dependency**:
   ```bash
   echo "playwright>=1.40.0" >> mcp_server/requirements.txt
   ```

2. **Install Playwright**:
   ```bash
   pip install -r mcp_server/requirements.txt
   playwright install chromium
   ```

3. **Copy new files**:
   - `mcp_server/browser_manager.py`
   - `mcp_server/server/tools/browser_tools.py`

4. **Modify existing files**:
   - `mcp_server/server/factory.py` (add BrowserManager)
   - `mcp_server/server/tools/__init__.py` (register browser tools)

5. **Update config**:
   - Add "browser" to enabled_tool_groups

6. **Restart MCP server**

### 11.2 Rollback Plan

- Remove "browser" from enabled_tool_groups
- Restart MCP server (gracefully degrades)
- No data loss (browser sessions are ephemeral)

---

## 12. Monitoring & Observability

### 12.1 Metrics to Track

- Active session count (`len(_sessions)`)
- Browser launch time (cold start)
- Tool call latency (per action)
- Session timeout cleanup count
- Error rate by action type

### 12.2 Logging

**Key Log Points**:
- Browser initialization (INFO)
- Session creation (DEBUG)
- Session cleanup (INFO)
- Tool call start/end (DEBUG)
- Errors with full traceback (ERROR)

**Format**: Structured logging with session_id, action, latency

---

## 13. Requirements Traceability Matrix

| Requirement | Component | Test |
|-------------|-----------|------|
| FR-1: Lifecycle | BrowserManager.__init__, initialize() | test_lazy_init |
| FR-2: Multi-Session | BrowserManager.get_session() | test_session_isolation |
| FR-3: Cleanup | BrowserManager.close_session(), _cleanup_stale() | test_cleanup |
| FR-4: Navigate | pos_browser action="navigate" | test_navigate |
| FR-5: Emulate Media | pos_browser action="emulate_media" | test_dark_mode |
| FR-6: Screenshot | pos_browser action="screenshot" | test_screenshot |
| FR-7: Viewport | pos_browser action="set_viewport" | test_viewport |
| FR-8: Console | pos_browser action="get_console" (stub) | test_console_stub |
| FR-9: Consolidated Tool | pos_browser() | test_all_actions |
| FR-10: Naming | Tool name "pos_browser" | test_tool_registered |
| FR-11: Integration | ServerFactory._create_browser_manager() | test_factory_integration |
| FR-12: Selective Loading | enabled_tool_groups check | test_selective_loading |
| NFR-1: Lazy Init | Not initialized until first call | test_no_init_on_startup |
| NFR-2: Reuse | Same page object returned | test_page_reuse |
| NFR-3: No Zombies | Process cleanup verified | test_no_zombie_processes |
| NFR-4: Thread Safety | asyncio.Lock usage | test_concurrent_access |
| NFR-5: Isolation | Separate contexts per session | test_no_state_leakage |
| NFR-6: Graceful Degradation | try/except all actions | test_error_handling |
| NFR-7: Error Messages | error + remediation fields | test_error_responses |
| NFR-8: Code Quality | Sphinx docstrings, type hints | manual_review |
| NFR-9: Testing | >80% coverage | pytest_coverage |
| NFR-10: Dependencies | playwright only | requirements_check |
| **FR-9: Click** | browser_tools._handle_click() | test_click_action |
| **FR-10: Type** | browser_tools._handle_type() | test_type_action |
| **FR-11: Fill** | browser_tools._handle_fill() | test_fill_action |
| **FR-12: Select** | browser_tools._handle_select() | test_select_action |
| **FR-13: Wait/Assert** | browser_tools._handle_wait() | test_wait_action |
| **FR-14: Query** | browser_tools._handle_query() | test_query_action |
| **FR-19: Test Execution** | test_runner.py (Phase 2) | test_test_execution |
| **FR-20: Network** | network_interceptor.py (Phase 2) | test_network_mock |
| **FR-21: Tabs** | tab_manager.py (Phase 2) | test_tab_management |
| **FR-22: Files** | file_handler.py (Phase 2) | test_file_operations |
| **FR-23: Cross-Browser** | BrowserManager.set_browser_type() | test_cross_browser |
| **FR-24: Headful** | BrowserManager(headless=False) | test_headful_mode |
| **FR-25-28: Tool Interface** | Tool registration | test_tool_registration |

**Total**: 28 Functional Requirements + 10 Non-Functional Requirements = 38 traced

---

## 14. Open Questions & Decisions

### 14.1 Resolved ✅

✅ **Architecture**: Per-session browsers (fully isolated)  
✅ **Scope**: Comprehensive Playwright (not limited)  
✅ **Granular vs Consolidated**: Consolidated (1 tool, 30+ actions)  
✅ **Tool Name**: `pos_browser` (avoids Cursor collision)  
✅ **Session Isolation**: Per-session browsers (failure isolation)  
✅ **Element Interaction**: IN SCOPE Phase 1 (click, type, fill, wait, assert)  
✅ **Test Execution**: IN SCOPE Phase 2 (testing contractor use case)  
✅ **Headless vs Headful**: Configurable (Phase 2)

### 14.2 Implementation Phasing (All In Scope)

**Phase 1 (Core)**: Navigate, click, type, fill, select, wait, assert, query, screenshot  
**Phase 2 (Advanced)**: Test execution, network, tabs, files, cross-browser, headful  
**Phase 3 (Power)**: Video, trace, PDF, accessibility, performance

---

**Phase 2 Complete** - Ready for Phase 3 (Task Breakdown)

