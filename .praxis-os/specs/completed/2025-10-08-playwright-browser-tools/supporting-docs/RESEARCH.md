# Playwright Browser Tools - Research & Design

**Date**: October 8, 2025
**Objective**: Design and implement Playwright browser automation tools for Agent OS Enhanced MCP server

---

## 🎯 Problem Statement

Current limitations with Cursor's Playwright MCP tool:
- ❌ Cannot emulate dark mode (`page.emulateMedia({ colorScheme: 'dark' })`)
- ❌ Cannot configure browser context (viewport, geolocation, permissions)
- ❌ Cannot manage persistent browser sessions across tool calls
- ❌ Limited API surface - only basic navigation and interaction
- ❌ No programmatic control over browser instances

**Impact**: Cannot properly test documentation sites, validate dark mode themes, or perform comprehensive browser automation tasks.

---

## 🔍 Research Findings

### 1. Playwright Python API

**Key Features We Need**:
```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # Browser launch with options
    browser = await p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    
    # Browser context with configuration
    context = await browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        color_scheme='dark',  # ⭐ Dark mode emulation
        geolocation={'latitude': 37.7749, 'longitude': -122.4194},
        permissions=['geolocation'],
        user_agent='Custom UA',
        locale='en-US',
        timezone_id='America/Los_Angeles'
    )
    
    # Page operations
    page = await context.new_page()
    await page.goto('https://example.com')
    await page.emulate_media(color_scheme='dark')  # ⭐ Runtime dark mode
    screenshot = await page.screenshot(full_page=True)
    await browser.close()
```

### 2. Existing Playwright MCP Implementations

**Microsoft's playwright-mcp (TypeScript)**:
- GitHub: https://github.com/microsoft/playwright-mcp
- Features: navigate, click, type, screenshot, console logs
- Architecture: Singleton browser instance, request/response model
- Limitations: TypeScript-only, basic API surface

**Playwright Plus Python MCP**:
- PyPI: https://pypi.org/project/playwright-mcp-server/
- Features: Similar to Microsoft's but in Python
- Architecture: Async-based, FastMCP compatible
- Considerations: License, dependencies, maintenance

**Key Learnings**:
1. **Singleton pattern**: Maintain one browser instance across tool calls
2. **Async architecture**: Playwright is async-first
3. **Session management**: Reuse contexts for efficiency
4. **Resource cleanup**: Proper browser shutdown on server exit

### 3. MCP Tool Patterns (Agent OS Enhanced)

From our codebase analysis:

**Tool Registration Pattern**:
```python
# File: mcp_server/server/tools/rag_tools.py
def register_rag_tools(mcp: Any, rag_engine: Any) -> int:
    """Register tools with MCP server."""
    
    @mcp.tool()
    async def search_standards(query: str, n_results: int = 5) -> Dict[str, Any]:
        """Tool implementation."""
        # ... tool logic ...
        return result
    
    return 1  # Number of tools registered
```

**Dependency Injection Pattern**:
```python
# File: mcp_server/server/factory.py
class ServerFactory:
    def _create_mcp_server(self, rag_engine, workflow_engine, ...) -> FastMCP:
        mcp = FastMCP("agent-os-rag")
        
        tool_count = register_all_tools(
            mcp=mcp,
            rag_engine=rag_engine,
            # ... inject dependencies ...
        )
        
        return mcp
```

**Key Patterns**:
- ✅ FastMCP decorator-based tool registration
- ✅ Dependency injection for components
- ✅ Async/await for I/O operations
- ✅ Optional HoneyHive tracing integration
- ✅ Structured logging

---

## 🏗️ Design Proposal

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│ MCP Server (FastMCP)                                     │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ RAG Engine   │  │ Workflow     │  │ Browser      │  │
│  │              │  │ Engine       │  │ Manager      │  │
│  └──────────────┘  └──────────────┘  └──────┬───────┘  │
│                                               │          │
│  ┌───────────────────────────────────────────┼────────┐ │
│  │ Browser Tools                              │        │ │
│  ├────────────────────────────────────────────────────┤ │
│  │ • browser_navigate()                      ▼        │ │
│  │ • browser_screenshot()            ┌────────────┐   │ │
│  │ • browser_click()                 │ Playwright │   │ │
│  │ • browser_emulate_media()         │ Instance   │   │ │
│  │ • browser_set_viewport()          │            │   │ │
│  │ • browser_get_console()           │ - Browser  │   │ │
│  │ • browser_close()                 │ - Context  │   │ │
│  └───────────────────────────────────│ - Page     │───┘ │
│                                       └────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### Component Design

**1. BrowserManager Class** (Singleton)
```python
# mcp_server/browser_manager.py

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any

class BrowserManager:
    """
    Manages persistent Playwright browser instance for MCP server.
    
    Provides singleton browser with configurable contexts and pages.
    Handles lifecycle management and resource cleanup.
    """
    
    def __init__(self):
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._config: Dict[str, Any] = {}
    
    async def initialize(self, headless: bool = True) -> None:
        """Initialize Playwright and launch browser."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=headless)
    
    async def get_or_create_context(self, **options) -> BrowserContext:
        """Get existing or create new browser context with options."""
        if self._context and self._config == options:
            return self._context
        
        # Close old context if config changed
        if self._context:
            await self._context.close()
        
        self._context = await self._browser.new_context(**options)
        self._config = options
        return self._context
    
    async def get_or_create_page(self) -> Page:
        """Get existing or create new page in current context."""
        if not self._page or self._page.is_closed():
            context = await self.get_or_create_context()
            self._page = await context.new_page()
        return self._page
    
    async def shutdown(self) -> None:
        """Clean shutdown of browser resources."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
```

**2. Browser Tools** (MCP Tool Registration)
```python
# mcp_server/server/tools/browser_tools.py

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


def register_browser_tools(mcp: Any, browser_manager: Any) -> int:
    """
    Register browser automation tools with MCP server.
    
    :param mcp: FastMCP server instance
    :param browser_manager: BrowserManager instance
    :return: Number of tools registered
    """
    tool_count = 0
    
    @mcp.tool()
    async def browser_navigate(
        url: str,
        wait_until: str = "load",
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Navigate to URL in browser.
        
        Args:
            url: Target URL to navigate to
            wait_until: Wait for 'load', 'domcontentloaded', or 'networkidle'
            timeout: Navigation timeout in milliseconds
        
        Returns:
            Page title, URL, and status
        """
        try:
            page = await browser_manager.get_or_create_page()
            await page.goto(url, wait_until=wait_until, timeout=timeout)
            
            return {
                "url": page.url,
                "title": await page.title(),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"browser_navigate failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    @mcp.tool()
    async def browser_emulate_media(
        color_scheme: Optional[str] = None,
        reduced_motion: Optional[str] = None,
        forced_colors: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Emulate media features (dark mode, reduced motion, etc).
        
        Args:
            color_scheme: 'light', 'dark', or 'no-preference'
            reduced_motion: 'reduce' or 'no-preference'
            forced_colors: 'active' or 'none'
        
        Returns:
            Configuration applied
        """
        try:
            page = await browser_manager.get_or_create_page()
            
            media_features = {}
            if color_scheme:
                media_features['colorScheme'] = color_scheme
            if reduced_motion:
                media_features['reducedMotion'] = reduced_motion
            if forced_colors:
                media_features['forcedColors'] = forced_colors
            
            await page.emulate_media(**media_features)
            
            return {
                "status": "success",
                "applied": media_features
            }
        except Exception as e:
            logger.error(f"browser_emulate_media failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    @mcp.tool()
    async def browser_screenshot(
        full_page: bool = False,
        path: Optional[str] = None,
        format: str = "png"
    ) -> Dict[str, Any]:
        """
        Take screenshot of current page.
        
        Args:
            full_page: Capture full scrollable page
            path: Optional file path to save screenshot
            format: 'png' or 'jpeg'
        
        Returns:
            Screenshot path or base64 data
        """
        try:
            page = await browser_manager.get_or_create_page()
            
            screenshot_options = {
                "full_page": full_page,
                "type": format
            }
            if path:
                screenshot_options["path"] = path
            
            screenshot_bytes = await page.screenshot(**screenshot_options)
            
            result = {"status": "success"}
            if path:
                result["path"] = path
            else:
                import base64
                result["data"] = base64.b64encode(screenshot_bytes).decode()
            
            return result
        except Exception as e:
            logger.error(f"browser_screenshot failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    @mcp.tool()
    async def browser_set_viewport(
        width: int = 1920,
        height: int = 1080
    ) -> Dict[str, Any]:
        """
        Set browser viewport size.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        
        Returns:
            Applied viewport dimensions
        """
        try:
            page = await browser_manager.get_or_create_page()
            await page.set_viewport_size({"width": width, "height": height})
            
            return {
                "status": "success",
                "viewport": {"width": width, "height": height}
            }
        except Exception as e:
            logger.error(f"browser_set_viewport failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    @mcp.tool()
    async def browser_get_console() -> Dict[str, Any]:
        """
        Get console messages from current page.
        
        Returns:
            List of console messages with type and text
        """
        try:
            page = await browser_manager.get_or_create_page()
            
            # TODO: Implement console message collection
            # Would need to add listener in page creation
            
            return {
                "status": "success",
                "messages": []
            }
        except Exception as e:
            logger.error(f"browser_get_console failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    @mcp.tool()
    async def browser_close() -> Dict[str, Any]:
        """
        Close current browser page/context.
        
        Returns:
            Closure status
        """
        try:
            await browser_manager.shutdown()
            return {"status": "success"}
        except Exception as e:
            logger.error(f"browser_close failed: {e}")
            return {"status": "error", "error": str(e)}
    
    tool_count += 1
    
    logger.info(f"Registered {tool_count} browser tools")
    return tool_count
```

**3. Integration with ServerFactory**
```python
# mcp_server/server/factory.py (modifications)

from ..browser_manager import BrowserManager
from .tools import register_all_tools

class ServerFactory:
    def create_server(self) -> FastMCP:
        # ... existing component creation ...
        
        # Create browser manager
        browser_manager = self._create_browser_manager()
        
        # Create MCP server
        mcp = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            browser_manager=browser_manager  # ⭐ New dependency
        )
        
        return mcp
    
    def _create_browser_manager(self) -> BrowserManager:
        """Create browser manager for Playwright automation."""
        logger.info("Creating browser manager...")
        manager = BrowserManager()
        # Initialize async (would need async context)
        return manager
```

---

## 🔧 Implementation Plan

### Phase 1: Core Browser Manager
1. Create `mcp_server/browser_manager.py`
2. Implement singleton browser lifecycle
3. Add context/page management
4. Add proper cleanup handlers

### Phase 2: Basic Browser Tools
1. Create `mcp_server/server/tools/browser_tools.py`
2. Implement:
   - `browser_navigate()`
   - `browser_emulate_media()` ⭐ (solves dark mode problem)
   - `browser_screenshot()`
   - `browser_set_viewport()`

### Phase 3: Integration
1. Modify `ServerFactory` to create `BrowserManager`
2. Register browser tools in `register_all_tools()`
3. Add to enabled tool groups configuration

### Phase 4: Testing & Documentation
1. Create unit tests for BrowserManager
2. Create integration tests for tools
3. Add usage examples to README
4. Update MCP tool documentation

---

## 📋 Dependencies

**New Dependencies** (`requirements.txt`):
```txt
playwright>=1.40.0  # Browser automation
```

**Install Browsers**:
```bash
playwright install chromium
```

**Size Impact**:
- Chromium: ~300MB
- Playwright Python: ~5MB

---

## 🎯 Success Criteria

1. ✅ Can emulate dark mode programmatically
2. ✅ Can configure viewport and browser context
3. ✅ Can take full-page screenshots
4. ✅ Browser instance persists across tool calls
5. ✅ Proper resource cleanup on server shutdown
6. ✅ Integration follows Agent OS patterns
7. ✅ Documentation updated

---

## 🚨 Open Questions

1. **Async initialization**: How to handle async BrowserManager.initialize() in ServerFactory?
   - Option A: Use `asyncio.run()` in factory
   - Option B: Lazy initialization on first tool call
   - **Recommendation**: Option B (lazy init)

2. **Multiple browser instances**: Should we support multiple concurrent browsers?
   - **Recommendation**: Start with singleton, add multi-instance later if needed

3. **Headless vs headed**: Should this be configurable?
   - **Recommendation**: Default headless, add config option

4. **Browser selection**: Just Chromium or support Firefox/WebKit?
   - **Recommendation**: Start with Chromium, add others later

5. **Tool group**: Create new "browser" tool group or add to existing?
   - **Recommendation**: New "browser" tool group for selective loading

---

## 📚 References

- [Playwright Python Docs](https://playwright.dev/python/)
- [Playwright Emulation API](https://playwright.dev/python/docs/emulation)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Agent OS Workflow Patterns](.praxis-os/standards/workflows/)

---

**Next Steps**: Create spec following Agent OS spec creation workflow

