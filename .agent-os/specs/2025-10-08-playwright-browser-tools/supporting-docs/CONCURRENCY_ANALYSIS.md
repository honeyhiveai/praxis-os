# Concurrency & Multi-Session Safety Analysis

**Critical Question**: What happens when multiple Cursor chats use the same MCP server simultaneously?

---

## 🚨 The Problem: Shared State Catastrophe

### Scenario: Multiple Chats, One MCP Server

```
Cursor IDE
├─> Chat Session A: "Test our docs in dark mode"
│   └─> Uses MCP server → BrowserManager (shared)
│
├─> Chat Session B: "Check homepage layout"
│   └─> Uses SAME MCP server → SAME BrowserManager ⚠️
│
└─> Chat Session C: "Screenshot login page"
    └─> Uses SAME MCP server → SAME BrowserManager ⚠️
```

### Race Condition Example

**Timeline of Disaster:**
```python
# Time T0: Chat A starts
Chat A: aos_browser(action="navigate", url="http://localhost:3000/docs")
# BrowserManager._page navigates to /docs

# Time T1: Chat B starts (before A finishes)
Chat B: aos_browser(action="navigate", url="http://localhost:3000/login")
# BrowserManager._page navigates to /login (SAME PAGE OBJECT)

# Time T2: Chat A continues
Chat A: aos_browser(action="emulate_media", color_scheme="dark")
# Sets dark mode on /login page (NOT /docs!)

# Time T3: Chat A takes screenshot
Chat A: aos_browser(action="screenshot", path="/tmp/docs.png")
# Screenshots /login page in dark mode, not /docs!
# ❌ WRONG RESULT
```

**Result**: Chat A gets a screenshot of the login page (from Chat B) instead of docs page.

### Current Architecture's Flaw

```python
class BrowserManager:
    """SINGLETON - shared across ALL MCP tool calls."""
    
    def __init__(self):
        self._page: Optional[Page] = None  # ⚠️ SINGLE SHARED PAGE
    
    async def get_or_create_page(self) -> Page:
        if not self._page:
            self._page = await self._context.new_page()
        return self._page  # ⚠️ EVERYONE GETS THE SAME PAGE
```

**Problem**: All chats share ONE page instance → **State corruption**.

---

## 🎯 MCP Server Invocation Model

### How Does Cursor Call MCP Servers?

**Key Question**: Is each MCP tool call:
1. A separate process invocation (stateless)?
2. Calls to a long-running server (stateful)?

**Answer**: **Long-running server** (stateful)

From our `mcp_server/__main__.py`:
```python
def main() -> None:
    # Create server
    mcp = factory.create_server()
    
    # Run with stdio transport - BLOCKS UNTIL SHUTDOWN
    mcp.run(transport='stdio')
```

**Implication**: 
- ✅ Server stays running
- ✅ Can maintain state (RAG index, workflow sessions, browser)
- ⚠️ **ALL tool calls from ALL chats go to SAME server instance**

### MCP Protocol: Session Identification

**Question**: Does MCP protocol provide session/chat IDs?

**Research Needed**: Check MCP spec for:
- Session identification headers
- Context/correlation IDs
- Request isolation mechanisms

**Preliminary Assessment**: MCP likely does NOT provide automatic session isolation.

---

## 🔧 Solution Strategies

### Strategy 1: Session-Based Browser Isolation ⭐ RECOMMENDED

**Concept**: Each chat gets its own browser context.

```python
class BrowserManager:
    """Manages multiple browser contexts, one per session."""
    
    def __init__(self):
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSession] = {}  # ⭐ Per-session state
        self._lock = asyncio.Lock()  # Thread safety
    
    async def get_session(self, session_id: str) -> BrowserSession:
        """Get or create isolated browser session."""
        async with self._lock:
            if session_id not in self._sessions:
                # Create new isolated context
                context = await self._browser.new_context()
                page = await context.new_page()
                self._sessions[session_id] = BrowserSession(
                    context=context,
                    page=page,
                    created_at=time.time()
                )
            return self._sessions[session_id]


@dataclass
class BrowserSession:
    """Isolated browser session with its own context and page."""
    context: BrowserContext
    page: Page
    created_at: float
    last_access: float = field(default_factory=time.time)


@mcp.tool()
async def aos_browser(
    action: str,
    session_id: Optional[str] = None,  # ⭐ REQUIRED for isolation
    **kwargs
) -> Dict[str, Any]:
    """
    Browser automation tool with session isolation.
    
    Args:
        action: Action to perform
        session_id: Session identifier for isolation (recommended)
        **kwargs: Action-specific parameters
    
    Notes:
        - Provide session_id to isolate browser state from other chats
        - Omitting session_id uses "default" session (shared state)
        - Each session has its own browser context and page
    """
    # Use default session if not provided (backward compatible)
    sid = session_id or "default"
    
    # Get isolated session
    session = await browser_manager.get_session(sid)
    page = session.page
    
    # Perform action on isolated page
    if action == "navigate":
        await page.goto(kwargs["url"])
        return {"status": "success", "session_id": sid}
    # ... etc
```

**Workflow with Sessions**:
```python
# Chat A: Generate unique session ID
session_a = "chat-a-1234"

Chat A: aos_browser(action="navigate", url="/docs", session_id=session_a)
Chat A: aos_browser(action="emulate_media", color_scheme="dark", session_id=session_a)
Chat A: aos_browser(action="screenshot", path="/tmp/docs.png", session_id=session_a)
# ✅ All operate on isolated session

# Chat B: Different session
session_b = "chat-b-5678"

Chat B: aos_browser(action="navigate", url="/login", session_id=session_b)
Chat B: aos_browser(action="screenshot", path="/tmp/login.png", session_id=session_b)
# ✅ Completely isolated from Chat A
```

**Pros**:
- ✅ Full isolation between chats
- ✅ Explicit session management
- ✅ Can have multiple pages per chat if needed
- ✅ Backward compatible (default session)

**Cons**:
- ⚠️ Requires AI agent to generate/track session IDs
- ⚠️ More complex API surface
- ⚠️ Resource cleanup complexity (stale sessions)

---

### Strategy 2: Automatic Session Detection

**Concept**: Detect caller context from MCP protocol.

```python
# Hypothetical: If MCP provides context
@mcp.tool()
async def aos_browser(
    action: str,
    context: Optional[MCPContext] = None,  # Injected by FastMCP
    **kwargs
) -> Dict[str, Any]:
    """Browser automation with automatic session detection."""
    
    # Extract session from MCP context
    session_id = context.session_id if context else "default"
    
    # Rest is same as Strategy 1
    session = await browser_manager.get_session(session_id)
    # ...
```

**Pros**:
- ✅ Automatic isolation
- ✅ No session_id parameter needed
- ✅ Transparent to AI agent

**Cons**:
- ❌ Depends on MCP protocol features (may not exist)
- ❌ Less explicit (harder to debug)

**Status**: Need to research if FastMCP/MCP provides context.

---

### Strategy 3: Single Session with Locks (NOT RECOMMENDED)

**Concept**: Use locks to serialize access.

```python
class BrowserManager:
    def __init__(self):
        self._page: Optional[Page] = None
        self._lock = asyncio.Lock()  # Serialize access
    
    async def get_page(self) -> Page:
        async with self._lock:  # Only one chat at a time
            if not self._page:
                self._page = await self._context.new_page()
            return self._page


@mcp.tool()
async def aos_browser(action: str, **kwargs) -> Dict[str, Any]:
    """Browser automation with lock-based serialization."""
    async with browser_manager._lock:  # Block other chats
        page = await browser_manager.get_page()
        # Perform action (blocks other chats until done)
```

**Pros**:
- ✅ Simple implementation
- ✅ No session management

**Cons**:
- ❌ Completely serializes all browser operations
- ❌ Chat A blocks Chat B even for independent operations
- ❌ Poor performance with multiple concurrent chats
- ❌ Still vulnerable to interleaving if one chat makes multiple calls

**Verdict**: ❌ **Do not use** - defeats purpose of concurrent chats.

---

### Strategy 4: Separate Browser Per Chat (Expensive)

**Concept**: Launch separate browser process per session.

```python
class BrowserManager:
    async def get_session(self, session_id: str) -> BrowserSession:
        if session_id not in self._sessions:
            # Launch SEPARATE browser process
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            self._sessions[session_id] = BrowserSession(
                playwright=playwright,
                browser=browser,  # Separate process
                context=context,
                page=page
            )
        return self._sessions[session_id]
```

**Pros**:
- ✅ Maximum isolation (separate processes)
- ✅ True parallelism (not just async)

**Cons**:
- ❌ Very expensive (300MB+ per browser)
- ❌ Slow startup (1-2 seconds per browser launch)
- ❌ Resource intensive (memory, CPU)

**Verdict**: ⚠️ **Overkill** - contexts are sufficient.

---

## 📊 Comparison: Isolation Strategies

| Strategy | Isolation | Performance | Complexity | Resource Use |
|----------|-----------|-------------|------------|--------------|
| Session-based contexts | ✅ Full | ✅ Good | ⚠️ Medium | ✅ Efficient |
| Auto session detection | ✅ Full | ✅ Good | ⚠️ Medium | ✅ Efficient |
| Single session + locks | ❌ None | ❌ Poor | ✅ Low | ✅ Efficient |
| Separate browsers | ✅ Maximum | ❌ Poor | ⚠️ Medium | ❌ Expensive |

---

## 🎯 Recommended Architecture

### Multi-Session BrowserManager

```python
# mcp_server/browser_manager.py

import asyncio
from dataclasses import dataclass, field
from typing import Dict, Optional
import time

@dataclass
class BrowserSession:
    """Isolated browser session."""
    context: BrowserContext
    page: Page
    created_at: float
    last_access: float = field(default_factory=time.time)
    
    async def cleanup(self):
        """Clean up session resources."""
        await self.page.close()
        await self.context.close()


class BrowserManager:
    """Manages multiple isolated browser sessions."""
    
    def __init__(self, session_timeout: int = 3600):
        self._playwright: Optional[Any] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()
        self._session_timeout = session_timeout  # 1 hour default
    
    async def initialize(self):
        """Initialize Playwright (lazy)."""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
    
    async def get_session(self, session_id: str = "default") -> BrowserSession:
        """
        Get or create isolated browser session.
        
        Each session has its own browser context and page,
        providing isolation between concurrent chats.
        """
        async with self._lock:
            # Clean up stale sessions first
            await self._cleanup_stale_sessions()
            
            # Get or create session
            if session_id not in self._sessions:
                # Ensure browser is initialized
                await self.initialize()
                
                # Create isolated context
                context = await self._browser.new_context()
                page = await context.new_page()
                
                self._sessions[session_id] = BrowserSession(
                    context=context,
                    page=page,
                    created_at=time.time()
                )
            
            # Update last access time
            self._sessions[session_id].last_access = time.time()
            
            return self._sessions[session_id]
    
    async def close_session(self, session_id: str):
        """Explicitly close a session."""
        async with self._lock:
            if session_id in self._sessions:
                await self._sessions[session_id].cleanup()
                del self._sessions[session_id]
    
    async def _cleanup_stale_sessions(self):
        """Clean up sessions that haven't been accessed recently."""
        now = time.time()
        stale = [
            sid for sid, session in self._sessions.items()
            if now - session.last_access > self._session_timeout
        ]
        
        for sid in stale:
            await self._sessions[sid].cleanup()
            del self._sessions[sid]
    
    async def shutdown(self):
        """Shutdown all sessions and browser."""
        async with self._lock:
            # Close all sessions
            for session in self._sessions.values():
                await session.cleanup()
            self._sessions.clear()
            
            # Close browser
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
```

### Updated Tool with Session Support

```python
@mcp.tool()
async def aos_browser(
    action: str,
    session_id: Optional[str] = None,
    url: Optional[str] = None,
    color_scheme: Optional[str] = None,
    # ... other params
) -> Dict[str, Any]:
    """
    Browser automation with session isolation.
    
    Session Management:
        - Provide session_id to isolate state from other concurrent chats
        - Each session has its own browser context and page
        - Sessions auto-cleanup after 1 hour of inactivity
        - Use action="close" to explicitly close a session
    
    Actions:
        navigate: Navigate to URL
        emulate_media: Set color scheme (dark mode)
        screenshot: Capture page screenshot
        set_viewport: Resize viewport
        close: Close session
    
    Examples:
        # Start isolated session
        aos_browser(action="navigate", url="/docs", session_id="test-dark-mode")
        aos_browser(action="emulate_media", color_scheme="dark", session_id="test-dark-mode")
        aos_browser(action="screenshot", path="/tmp/dark.png", session_id="test-dark-mode")
        aos_browser(action="close", session_id="test-dark-mode")
    
    Args:
        action: Action to perform
        session_id: Optional session ID for isolation (default: "default")
        url: Target URL (for navigate)
        color_scheme: Color scheme (for emulate_media)
        ... [other params]
    
    Returns:
        Action-specific result with session_id
    """
    try:
        # Get isolated session
        sid = session_id or "default"
        session = await browser_manager.get_session(sid)
        page = session.page
        
        # Handle close action specially
        if action == "close":
            await browser_manager.close_session(sid)
            return {"status": "success", "message": f"Session {sid} closed"}
        
        # Dispatch to action handlers
        if action == "navigate":
            await page.goto(url, wait_until="load", timeout=30000)
            return {
                "status": "success",
                "session_id": sid,
                "url": page.url,
                "title": await page.title()
            }
        
        elif action == "emulate_media":
            media_features = {}
            if color_scheme:
                media_features['colorScheme'] = color_scheme
            await page.emulate_media(**media_features)
            return {
                "status": "success",
                "session_id": sid,
                "applied": media_features
            }
        
        elif action == "screenshot":
            # ... screenshot logic
            return {
                "status": "success",
                "session_id": sid,
                "path": screenshot_path
            }
        
        # ... other actions
    
    except Exception as e:
        logger.error(f"aos_browser action '{action}' failed: {e}")
        return {"status": "error", "error": str(e)}
```

---

## 🔐 Thread Safety Considerations

### AsyncIO Locks
```python
self._lock = asyncio.Lock()  # Async-safe lock

async with self._lock:
    # Critical section (session creation/cleanup)
    pass
```

**Why**: Protect shared state (`_sessions` dict) from race conditions.

### Browser Context Isolation
```python
# Playwright browser contexts are isolated by design
context_a = await browser.new_context()  # Isolated cookies, storage
context_b = await browser.new_context()  # Completely separate

# Pages within same context share state
page1 = await context_a.new_page()
page2 = await context_a.new_page()  # Shares cookies with page1
```

**Result**: Each session gets isolated context → No state leakage.

---

## 📋 Usage Patterns

### Pattern 1: AI Agent Generates Session ID

```python
# AI agent logic (implicit in its reasoning):
session_id = f"chat-{random_id()}"  # Generate unique ID

# Use for all operations in this workflow
aos_browser(action="navigate", url="/docs", session_id=session_id)
aos_browser(action="emulate_media", color_scheme="dark", session_id=session_id)
aos_browser(action="screenshot", path="/tmp/test.png", session_id=session_id)
aos_browser(action="close", session_id=session_id)
```

### Pattern 2: Human Provides Session ID

```
Human: "Test dark mode on docs site, use session 'dark-mode-test'"

AI: 
aos_browser(action="navigate", url="/docs", session_id="dark-mode-test")
aos_browser(action="emulate_media", color_scheme="dark", session_id="dark-mode-test")
...
```

### Pattern 3: Default Session (Backward Compatible)

```python
# Omit session_id → uses "default" session
aos_browser(action="navigate", url="/docs")
# Works, but shared with other chats using default
```

---

## ✅ Recommended Implementation

**Use Strategy 1: Session-Based Browser Contexts**

**Checklist**:
- [x] Multi-session `BrowserManager` with isolated contexts
- [x] Optional `session_id` parameter (defaults to "default")
- [x] AsyncIO locks for thread safety
- [x] Automatic stale session cleanup (1 hour timeout)
- [x] Explicit `close` action for manual cleanup
- [x] Return `session_id` in all responses for tracking

**Benefits**:
- ✅ Full isolation between concurrent chats
- ✅ Resource efficient (shared browser process)
- ✅ Automatic cleanup prevents memory leaks
- ✅ Backward compatible (default session)
- ✅ Explicit control when needed

**Trade-offs**:
- ⚠️ AI agent must manage session IDs (extra cognitive load)
- ⚠️ Slightly more complex API
- ⚠️ Stale session cleanup adds complexity

---

## 🚀 Next Steps

1. **Update RESEARCH.md** - Add session isolation to `BrowserManager` design
2. **Update TOOL_CONSOLIDATION.md** - Add `session_id` parameter to examples
3. **Update SESSION_MANAGEMENT.md** - Add multi-session section
4. **Create test scenarios** - Verify isolation between sessions
5. **Document session patterns** - How AI should use sessions

---

**Session isolation is CRITICAL for concurrent chat safety!** 🔒

