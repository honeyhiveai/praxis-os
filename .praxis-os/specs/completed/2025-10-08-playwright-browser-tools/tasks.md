# Implementation Tasks
# Browser Automation Tool for prAxIs OS MCP Server

**Version**: 1.0  
**Date**: October 8, 2025  
**Requirements**: See `srd.md`  
**Design**: See `specs.md`  
**Phase**: 3 of 6 (spec_creation_v1)

---

## Overview

This document breaks down the comprehensive browser automation implementation into phases:

**Phase 1: Core Infrastructure** (4-6 hours)
- BrowserManager with per-session browsers
- Session management and cleanup

**Phase 2: Core Actions** (12-15 hours) ⭐ EXPANDED
- Navigation and inspection (original scope)
- **Element interaction** (click, type, fill, select)
- **Waiting and assertions** (wait_for, query)
- Comprehensive action handler implementation

**Phase 3: Testing & Validation** (6-8 hours) ⭐ EXPANDED
- Unit tests for all action handlers
- Integration tests for workflows
- Session isolation validation

**Phase 4: Documentation & Deployment** (2-3 hours)
- Installation docs
- Usage examples
- Deployment procedures

**Phase 5: Advanced Features (Phase 2 Scope)** (15-20 hours)
- Test script execution (FR-19 - testing contractor)
- Network interception (FR-20)
- Tab management (FR-21)
- File I/O (FR-22)
- Cross-browser support (FR-23)
- Headful mode (FR-24)

**Total Estimated Time**: 
- **Phase 1-4 (Core)**: 24-32 hours
- **Phase 5 (Advanced)**: +15-20 hours
- **Grand Total**: 39-52 hours

**Critical Path**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 (sequential)

---

## Phase 1: Core Infrastructure (4-6 hours)

**Goal**: Implement BrowserManager with session isolation and concurrency safety

### Task 1.1: Create BrowserSession Data Model (Per-Session Architecture)

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: None  
**Priority**: MUST HAVE

**Description**: Define BrowserSession dataclass for fully isolated session (per-session browser)

**Architecture Note**: Each session gets its own Playwright + Chromium process (not shared browser)

**Acceptance Criteria**:
- [ ] Dataclass with `playwright`, `browser`, `page`, `created_at`, `last_access` fields
- [ ] Type hints: `playwright: Any`, `browser: Browser`, `page: Page`, timestamps: `float`
- [ ] `cleanup()` async method closes page, browser, AND stops playwright
- [ ] Sphinx docstrings with architecture notes (per-session isolation)
- [ ] Default factory for `last_access` (time.time)

**Validation**:
```python
# Can create session with own browser
session = BrowserSession(
    playwright=pw, 
    browser=browser, 
    page=page, 
    created_at=time.time()
)
assert session.last_access > 0
assert session.browser is not None  # Own browser process

# Cleanup kills browser process
await session.cleanup()
assert page.is_closed()
assert browser process terminated
```

**Traceability**: FR-2, NFR-5 (per-session isolation for AI agent UX)

---

### Task 1.2: Implement BrowserManager (Per-Session Architecture)

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Task 1.1  
**Priority**: MUST HAVE

**Description**: Create thread-safe BrowserManager for per-session browsers (NO shared browser)

**Architecture Note**: Manager only tracks sessions; each session creates its own browser

**Acceptance Criteria**:
- [ ] `__init__()` accepts `session_timeout` parameter (default 3600)
- [ ] Private fields: `_sessions` (Dict), `_lock` (asyncio.Lock) - NO `_browser` or `_playwright`!
- [ ] Sphinx docstrings emphasizing per-session isolation architecture
- [ ] No shared browser state (simpler than singleton approach)
- [ ] All public methods are async

**Validation**:
```python
# Initialization is lightweight (no shared browser)
manager = BrowserManager()
assert not hasattr(manager, '_browser')  # No shared browser!

# Each session creates own browser
session1 = await manager.get_session("test-1")
session2 = await manager.get_session("test-2")
assert session1.browser is not session2.browser  # Different browser processes
```

**Traceability**: FR-1, NFR-1, NFR-4 (simplified by per-session architecture)

---

### Task 1.3: Implement get_session() with Per-Session Browser Creation

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 2 hours (more complex than singleton approach)  
**Dependencies**: Task 1.2  
**Priority**: MUST HAVE

**Description**: Thread-safe session retrieval with per-session browser launch

**Architecture Note**: Each new session launches its own Playwright + Chromium process

**Acceptance Criteria**:
- [ ] Async method `get_session(session_id: str = "default")`
- [ ] Acquires `_lock` before accessing `_sessions` dict
- [ ] For NEW session: Launches `async_playwright().start()`
- [ ] For NEW session: Launches `playwright.chromium.launch(headless=True)`
- [ ] For NEW session: Creates page from new browser
- [ ] For EXISTING session: Updates `last_access` timestamp, returns existing
- [ ] Calls `_cleanup_stale_sessions()` before creating new
- [ ] Returns BrowserSession with own playwright + browser + page
- [ ] Logs INFO "Session created: {id} with new browser process (total: {count})"
- [ ] Handles browser launch failures with remediation message

**Validation**:
```python
# Creates new session with own browser
session1 = await manager.get_session("test-1")
assert "test-1" in manager._sessions
assert session1.playwright is not None
assert session1.browser is not None

# Reuses existing session
session2 = await manager.get_session("test-1")
assert session1.page is session2.page
assert session1.browser is session2.browser  # Same browser

# Different session IDs get different browsers (full isolation)
session3 = await manager.get_session("test-2")
assert session3.browser is not session1.browser  # Different browser processes!
assert session3.playwright is not session1.playwright  # Different Playwright instances!
```

**Traceability**: FR-2, NFR-1, NFR-2, NFR-4, NFR-5 (per-session isolation)

---

### Task 1.4: Implement Stale Session Cleanup

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 1.3  
**Priority**: MUST HAVE

**Description**: Auto-cleanup of idle sessions (kills browser processes)

**Acceptance Criteria**:
- [ ] Async method `_cleanup_stale_sessions()` (private)
- [ ] Calculates `now - last_access` for each session
- [ ] Closes and removes sessions where delta > `_session_timeout`
- [ ] Calls `session.cleanup()` which kills browser process
- [ ] Logs INFO "Cleaned up stale session: {session_id} (idle for {delta}s)"
- [ ] Handles cleanup errors gracefully (logs, continues to next)
- [ ] Called automatically by `get_session()` before creating new

**Validation**:
```python
# Create session
session = await manager.get_session("test")
assert session.browser is not None

# Manually set old timestamp
manager._sessions["test"].last_access = time.time() - 7200  # 2 hours ago

# Cleanup removes it and kills browser
await manager._cleanup_stale_sessions()
assert "test" not in manager._sessions
assert session.browser process killed  # Verify no zombie
```

**Traceability**: FR-3, NFR-3, NFR-6

---

### Task 1.5: Implement Explicit Session Close

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 1.3  
**Priority**: MUST HAVE

**Description**: Explicit session closure (kills browser process)

**Acceptance Criteria**:
- [ ] Async method `close_session(session_id: str)`
- [ ] Acquires `_lock` before dict access
- [ ] Calls `session.cleanup()` which stops playwright + closes browser
- [ ] Removes session from `_sessions` dict
- [ ] Logs INFO "Session closed: {session_id}, browser process terminated"
- [ ] Does nothing if session not found (idempotent)

**Validation**:
```python
# Create and close session
session = await manager.get_session("test")
browser_pid = session.browser.process_id  # Track process

await manager.close_session("test")
assert "test" not in manager._sessions
assert session.page.is_closed()
assert browser_pid process no longer exists  # Verify cleanup

# Closing non-existent session doesn't error
await manager.close_session("nonexistent")  # No exception
```

**Traceability**: FR-3, NFR-6

---

### Task 1.6: Implement Graceful Shutdown

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 1.5  
**Priority**: MUST HAVE

**Description**: Clean shutdown of all sessions (kills all browser processes)

**Acceptance Criteria**:
- [ ] Async method `shutdown()`
- [ ] Closes all sessions via `close_session()` (kills all browsers)
- [ ] Logs INFO "Browser manager shutdown complete ({count} sessions closed)"
- [ ] Idempotent (can call multiple times)
- [ ] No zombie browser processes remain

**Validation**:
```python
# Create sessions
await manager.get_session("test-1")
await manager.get_session("test-2")
initial_process_count = count_chromium_processes()

# Shutdown cleans everything
await manager.shutdown()
assert len(manager._sessions) == 0
assert count_chromium_processes() < initial_process_count  # Processes killed

# Can call again safely
await manager.shutdown()  # No exception
```

**Traceability**: FR-3, NFR-3, NFR-6

---

**Phase 1 Deliverables**:
- `mcp_server/browser_manager.py` (complete)
- BrowserSession dataclass (with playwright + browser per session)
- BrowserManager class (6 methods: __init__, get_session, _cleanup_stale, close_session, shutdown)

**Phase 1 Validation Gate**:
- [ ] All 6 tasks complete (Task 1.1-1.6)
- [ ] File runs without syntax errors
- [ ] All type hints present
- [ ] All docstrings present (Sphinx format, emphasize per-session architecture)
- [ ] Manual test: Can create session, each has own browser, cleanup kills processes
- [ ] Architecture verified: No shared browser state, full isolation

---

## Phase 2: Core Actions Implementation (12-15 hours)

**Goal**: Implement comprehensive pos_browser tool with 30+ actions

**Scope**: Navigation, inspection, interaction, waiting, context control, session management

### Task 2.1: Create browser_tools.py Skeleton

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Phase 1 complete  
**Priority**: MUST HAVE

**Description**: Create tool registration module with pos_browser skeleton

**Acceptance Criteria**:
- [ ] Module-level docstring
- [ ] Import BrowserManager from mcp_server.browser_manager
- [ ] Function `register_browser_tools(mcp, browser_manager) -> int`
- [ ] Skeleton `@mcp.tool() async def pos_browser()` with all parameters
- [ ] Return 1 (tool count)
- [ ] Comprehensive docstring with all actions, examples

**Validation**:
```python
# Can import
from mcp_server.server.tools.browser_tools import register_browser_tools

# Can call
count = register_browser_tools(mcp, manager)
assert count == 1
```

**Traceability**: FR-9, FR-10, FR-11

---

### Task 2.2: Implement Navigate Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement page navigation with configurable wait

**Acceptance Criteria**:
- [ ] Validates `url` parameter is required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Calls `page.goto(url, wait_until=wait_until, timeout=timeout)`
- [ ] Returns success dict with url, title, status
- [ ] Catches TimeoutError, returns error dict with remediation
- [ ] Logs DEBUG "Navigate: {url}"

**Validation**:
```python
# Success case
result = await pos_browser(action="navigate", url="https://example.com", session_id="test")
assert result["status"] == "success"
assert result["url"] == "https://example.com"
assert "title" in result

# Timeout case
result = await pos_browser(action="navigate", url="https://slow.com", timeout=100)
assert result["status"] == "error"
assert "timeout" in result["error"].lower()
```

**Traceability**: FR-4, NFR-6, NFR-7

---

### Task 2.3: Implement Emulate Media Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement media feature emulation (dark mode, etc)

**Acceptance Criteria**:
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Calls `page.emulate_media(color_scheme=..., reduced_motion=...)`
- [ ] Supports: color_scheme (light/dark/no-preference), reduced_motion (reduce/no-preference)
- [ ] Returns success dict with applied features
- [ ] Logs DEBUG "Emulate media: {color_scheme}"

**Validation**:
```python
# Set dark mode
result = await pos_browser(action="emulate_media", color_scheme="dark", session_id="test")
assert result["status"] == "success"
assert result["color_scheme"] == "dark"

# Page responds to dark mode (manual visual test)
```

**Traceability**: FR-5

---

### Task 2.4: Implement Screenshot Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement screenshot capture with path validation

**Acceptance Criteria**:
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Validates `screenshot_path` is in workspace or /tmp (security)
- [ ] Calls `page.screenshot(full_page=..., path=..., type=...)`
- [ ] Returns success dict with saved path
- [ ] Falls back to base64 if no path specified
- [ ] Logs INFO "Screenshot saved: {path}"

**Validation**:
```python
# Save to file
result = await pos_browser(
    action="screenshot",
    screenshot_path="/tmp/test.png",
    screenshot_full_page=True,
    session_id="test"
)
assert result["status"] == "success"
assert Path("/tmp/test.png").exists()

# Base64 mode
result = await pos_browser(action="screenshot", session_id="test")
assert "base64" in result
```

**Traceability**: FR-6, NFR-6

---

### Task 2.5: Implement Viewport & Console Actions

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 2.1  
**Priority**: SHOULD HAVE

**Description**: Implement set_viewport and get_console (stub) actions

**Acceptance Criteria**:
- [ ] `set_viewport`: Calls `page.set_viewport_size(width=..., height=...)`
- [ ] `set_viewport`: Returns success dict with applied dimensions
- [ ] `get_console`: Stub implementation returns empty list + note
- [ ] Logs DEBUG for both actions

**Validation**:
```python
# Viewport
result = await pos_browser(action="set_viewport", viewport_width=1024, viewport_height=768, session_id="test")
assert result["status"] == "success"
assert result["viewport"] == {"width": 1024, "height": 768}

# Console (stub)
result = await pos_browser(action="get_console", session_id="test")
assert result["console_messages"] == []
```

**Traceability**: FR-7, FR-8

---

### Task 2.6: Implement Close Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 15 minutes  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement explicit session close action

**Acceptance Criteria**:
- [ ] Calls `browser_manager.close_session(session_id)`
- [ ] Returns success dict with closed session_id
- [ ] Logs INFO "Session closed via tool: {session_id}"

**Validation**:
```python
# Close session
result = await pos_browser(action="close", session_id="test")
assert result["status"] == "success"
assert result["session_id"] == "test"

# Session no longer exists
assert "test" not in browser_manager._sessions
```

**Traceability**: FR-3, FR-9

---

### Task 2.7: Integrate with ServerFactory

**File**: `mcp_server/server/factory.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Add BrowserManager to dependency injection

**Acceptance Criteria**:
- [ ] Add `_create_browser_manager()` method
- [ ] Call in `create_server()`, pass to `_create_mcp_server()`
- [ ] Pass `browser_manager` to `register_all_tools()`
- [ ] Logs INFO "Creating browser manager..."

**Validation**:
```python
# Factory creates browser manager
factory = ServerFactory(config)
server = factory.create_server()

# Browser manager exists
assert hasattr(server, "_browser_manager") or browser_manager passed to tools
```

**Traceability**: FR-11

---

### Task 2.8: Register Tool Conditionally

**File**: `mcp_server/server/tools/__init__.py`  
**Estimated Time**: 15 minutes  
**Dependencies**: Task 2.7  
**Priority**: MUST HAVE

**Description**: Register browser tools in register_all_tools()

**Acceptance Criteria**:
- [ ] Add `browser_manager` optional parameter to `register_all_tools()`
- [ ] Add "browser" to default `enabled_groups`
- [ ] Check if "browser" in enabled_groups and browser_manager not None
- [ ] Import and call `register_browser_tools(mcp, browser_manager)`
- [ ] Log tool count

**Validation**:
```python
# With browser enabled
count = register_all_tools(mcp, ..., browser_manager=manager, enabled_groups=["rag", "workflow", "browser"])
assert count >= 9  # 8 existing + 1 browser

# Without browser
count = register_all_tools(mcp, ..., enabled_groups=["rag", "workflow"])
assert count == 8  # No browser tool
```

**Traceability**: FR-11, FR-12

---

### Task 2.9: Implement Click Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement element clicking with selector strategies

**Acceptance Criteria**:
- [ ] Validates `selector` parameter is required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `button` parameter: left (default), right, middle
- [ ] Supports `click_count` parameter (default: 1)
- [ ] Supports `modifiers` parameter: Shift, Control, Alt, Meta
- [ ] Calls `page.click(selector, button=..., click_count=..., modifiers=...)`
- [ ] Handles `TimeoutError` (element not found), returns remediation
- [ ] Returns success dict with selector, element info
- [ ] Logs DEBUG "Click: {selector} (button={button})"

**Validation**:
```python
# Success case
result = await pos_browser(action="click", selector="button#submit", session_id="test")
assert result["status"] == "success"
assert result["selector"] == "button#submit"

# Element not found
result = await pos_browser(action="click", selector="#nonexistent")
assert result["status"] == "error"
assert "not found" in result["error"].lower()

# Right click
result = await pos_browser(action="click", selector=".menu", button="right")
assert result["button"] == "right"
```

**Traceability**: FR-9 (element interaction)

---

### Task 2.10: Implement Type Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement keyboard typing with delay simulation

**Acceptance Criteria**:
- [ ] Validates `text` parameter is required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `delay` parameter (ms between keystrokes, default: 0)
- [ ] Calls `page.keyboard.type(text, delay=delay)`
- [ ] Returns success dict with text length, delay
- [ ] Logs DEBUG "Type: {len(text)} characters (delay={delay}ms)"

**Validation**:
```python
# Success case
result = await pos_browser(action="type", text="Hello World", session_id="test")
assert result["status"] == "success"
assert result["characters_typed"] == 11

# With delay (human-like typing)
result = await pos_browser(action="type", text="test", delay=50)
assert result["delay"] == 50
```

**Traceability**: FR-10 (element interaction)

---

### Task 2.11: Implement Fill Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement form field filling with validation

**Acceptance Criteria**:
- [ ] Validates `selector` and `value` parameters are required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `force` parameter (bypass actionability checks, default: False)
- [ ] Calls `page.fill(selector, value, force=force)`
- [ ] Handles `TimeoutError` (element not found)
- [ ] Handles `Error` (not fillable element), returns remediation
- [ ] Returns success dict with selector, value length, element type
- [ ] Logs DEBUG "Fill: {selector} ({len(value)} chars)"

**Validation**:
```python
# Success case
result = await pos_browser(action="fill", selector="input#email", value="test@example.com")
assert result["status"] == "success"
assert result["selector"] == "input#email"
assert result["value_length"] == 16

# Not fillable
result = await pos_browser(action="fill", selector="div#output", value="test")
assert result["status"] == "error"
assert "not fillable" in result["error"].lower()
```

**Traceability**: FR-11 (form interaction)

---

### Task 2.12: Implement Select Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement dropdown/select element interaction

**Acceptance Criteria**:
- [ ] Validates `selector` parameter is required
- [ ] Validates one of `value`, `label`, or `index` is provided
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Calls `page.select_option(selector, value=..., label=..., index=...)`
- [ ] Handles `TimeoutError` (element not found)
- [ ] Handles `Error` (not select element), returns remediation
- [ ] Returns success dict with selector, selected values
- [ ] Logs DEBUG "Select: {selector} (value={value})"

**Validation**:
```python
# Select by value
result = await pos_browser(action="select", selector="select#country", value="US")
assert result["status"] == "success"
assert "US" in result["selected_values"]

# Select by label
result = await pos_browser(action="select", selector="select#country", label="United States")
assert result["status"] == "success"

# Select by index
result = await pos_browser(action="select", selector="select#country", index=0)
assert result["status"] == "success"
```

**Traceability**: FR-12 (form interaction)

---

### Task 2.13: Implement Wait/Assert Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement element waiting with multiple strategies

**Acceptance Criteria**:
- [ ] Validates `selector` parameter is required
- [ ] Validates `wait_for` parameter: visible, hidden, attached, detached
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `timeout` parameter (ms, default: 30000)
- [ ] Calls appropriate method:
  - `wait_for="visible"`: `page.wait_for_selector(selector, state="visible")`
  - `wait_for="hidden"`: `page.wait_for_selector(selector, state="hidden")`
  - `wait_for="attached"`: `page.wait_for_selector(selector, state="attached")`
  - `wait_for="detached"`: `page.wait_for_selector(selector, state="detached")`
- [ ] Handles `TimeoutError`, returns clear message
- [ ] Returns success dict with selector, wait_for, duration
- [ ] Logs DEBUG "Wait: {selector} {wait_for} (timeout={timeout}ms)"

**Validation**:
```python
# Wait for visible
result = await pos_browser(action="wait", selector="#modal", wait_for="visible", timeout=5000)
assert result["status"] == "success"
assert result["wait_for"] == "visible"
assert result["duration_ms"] > 0

# Timeout case
result = await pos_browser(action="wait", selector="#never-appears", wait_for="visible", timeout=1000)
assert result["status"] == "error"
assert "timeout" in result["error"].lower()
```

**Traceability**: FR-13 (waiting strategies)

---

### Task 2.14: Implement Query Element Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement element inspection and property retrieval

**Acceptance Criteria**:
- [ ] Validates `selector` parameter is required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `properties` parameter: text, value, attribute, visible, enabled, checked
- [ ] Returns dict with requested properties:
  - `text`: `element.text_content()`
  - `value`: `element.input_value()`
  - `attribute.{name}`: `element.get_attribute(name)`
  - `visible`: `element.is_visible()`
  - `enabled`: `element.is_enabled()`
  - `checked`: `element.is_checked()`
- [ ] Handles `TimeoutError` (element not found)
- [ ] Returns success dict with selector, properties dict
- [ ] Logs DEBUG "Query: {selector} ({len(properties)} properties)"

**Validation**:
```python
# Query multiple properties
result = await pos_browser(
    action="query", 
    selector="input#email", 
    properties=["text", "value", "visible", "enabled"]
)
assert result["status"] == "success"
assert "properties" in result
assert "visible" in result["properties"]
assert "value" in result["properties"]

# Query attribute
result = await pos_browser(
    action="query", 
    selector="a#link", 
    properties=["attribute.href", "text"]
)
assert "href" in result["properties"]
```

**Traceability**: FR-14 (element inspection)

---

### Task 2.15: Implement Evaluate JavaScript Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Task 2.1  
**Priority**: MUST HAVE

**Description**: Implement arbitrary JavaScript execution in page context

**Acceptance Criteria**:
- [ ] Validates `script` parameter is required
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Supports `args` parameter (JSON-serializable array)
- [ ] Calls `page.evaluate(script, *args)`
- [ ] Handles JavaScript errors, returns error dict
- [ ] Returns success dict with result (JSON-serializable)
- [ ] Logs DEBUG "Evaluate: {len(script)} chars"
- [ ] Security note in docstring about script execution

**Validation**:
```python
# Simple evaluation
result = await pos_browser(action="evaluate", script="document.title")
assert result["status"] == "success"
assert "result" in result

# With arguments
result = await pos_browser(
    action="evaluate", 
    script="(x, y) => x + y", 
    args=[5, 3]
)
assert result["result"] == 8

# JavaScript error
result = await pos_browser(action="evaluate", script="throw new Error('test')")
assert result["status"] == "error"
```

**Traceability**: FR-5 (page interaction)

---

### Task 2.16: Implement Get Cookies Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 2.1  
**Priority**: SHOULD HAVE

**Description**: Implement cookie retrieval

**Acceptance Criteria**:
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Calls `page.context.cookies()`
- [ ] Returns success dict with cookies array
- [ ] Each cookie has: name, value, domain, path, expires, httpOnly, secure, sameSite
- [ ] Logs DEBUG "Get cookies: {count} found"

**Validation**:
```python
# Get all cookies
result = await pos_browser(action="get_cookies", session_id="test")
assert result["status"] == "success"
assert "cookies" in result
assert isinstance(result["cookies"], list)
```

**Traceability**: FR-8 (browser state)

---

### Task 2.17: Implement Set Cookies Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 2.1  
**Priority**: SHOULD HAVE

**Description**: Implement cookie setting

**Acceptance Criteria**:
- [ ] Validates `cookies` parameter is required (array of cookie dicts)
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Validates each cookie has required fields: name, value, domain or url
- [ ] Calls `page.context.add_cookies(cookies)`
- [ ] Handles validation errors, returns remediation
- [ ] Returns success dict with count of cookies set
- [ ] Logs DEBUG "Set cookies: {count} added"

**Validation**:
```python
# Set cookies
result = await pos_browser(
    action="set_cookies",
    cookies=[
        {"name": "session", "value": "abc123", "url": "https://example.com"}
    ]
)
assert result["status"] == "success"
assert result["cookies_set"] == 1
```

**Traceability**: FR-8 (browser state)

---

### Task 2.18: Implement Get Local Storage Action

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 2.1  
**Priority**: SHOULD HAVE

**Description**: Implement local storage retrieval via JavaScript

**Acceptance Criteria**:
- [ ] Gets session via `browser_manager.get_session(session_id)`
- [ ] Executes: `page.evaluate("() => Object.entries(localStorage)")`
- [ ] Returns success dict with storage dict
- [ ] Logs DEBUG "Get local storage: {count} items"

**Validation**:
```python
# Get local storage
result = await pos_browser(action="get_local_storage", session_id="test")
assert result["status"] == "success"
assert "storage" in result
assert isinstance(result["storage"], dict)
```

**Traceability**: FR-8 (browser state)

---

**Phase 2 Deliverables**:
- `mcp_server/server/tools/browser_tools.py` (complete with 20+ actions)
- Modified `mcp_server/server/factory.py`
- Modified `mcp_server/server/tools/__init__.py`
- Action handlers:
  - **Navigation**: navigate
  - **Inspection**: screenshot, console, query, evaluate, get_cookies, get_local_storage
  - **Interaction**: click, type, fill, select
  - **Waiting**: wait (4 strategies)
  - **Context**: emulate_media, viewport, set_cookies
  - **Session**: close

**Phase 2 Validation Gate**:
- [ ] All 18 tasks complete (Task 2.1-2.18)
- [ ] `pos_browser` tool registered and callable
- [ ] All 20+ actions functional
- [ ] MCP server starts without errors
- [ ] Tool appears in tool list
- [ ] Manual test: Full workflow (navigate, click, fill, wait, query, screenshot, close)

---

## Phase 3: Testing & Validation (6-8 hours)

**Goal**: Comprehensive test coverage for reliability (40+ tests)

### Task 3.1: Unit Tests - BrowserManager Basics

**File**: `tests/unit/test_browser_manager.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Phase 1 complete  
**Priority**: MUST HAVE

**Description**: Test BrowserManager initialization and per-session lifecycle

**Test Cases**:
- `test_init_lightweight` - No browser created at init (no shared browser)
- `test_get_session_creates_new_browser` - New session gets own browser process
- `test_get_session_reuses_existing` - Same session reuses browser
- `test_different_sessions_isolated` - Different sessions have different browsers
- `test_close_session_kills_browser` - Session cleanup kills browser process
- `test_shutdown_kills_all_browsers` - Shutdown kills all processes
- `test_shutdown` - All resources released

**Acceptance Criteria**:
- [ ] All 6 tests pass
- [ ] Uses pytest-asyncio for async tests
- [ ] Mocks Playwright (no real browser)
- [ ] >80% coverage of BrowserManager

**Traceability**: FR-1, FR-2, FR-3, NFR-9

---

### Task 3.2: Unit Tests - Session Isolation

**File**: `tests/unit/test_browser_manager.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 3.1  
**Priority**: MUST HAVE

**Description**: Test multi-session isolation and concurrency

**Test Cases**:
- `test_multiple_sessions_isolated` - Different contexts
- `test_concurrent_get_session` - Thread safety with asyncio.gather
- `test_no_state_leakage` - Cookies/storage separate

**Acceptance Criteria**:
- [ ] All 3 tests pass
- [ ] Uses concurrent calls to test locking
- [ ] Verifies distinct contexts per session

**Traceability**: FR-2, NFR-4, NFR-5

---

### Task 3.3: Unit Tests - Stale Session Cleanup

**File**: `tests/unit/test_browser_manager.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 3.1  
**Priority**: MUST HAVE

**Description**: Test auto-cleanup of idle sessions

**Test Cases**:
- `test_cleanup_stale_sessions` - Old sessions removed
- `test_cleanup_preserves_active` - Recent sessions kept
- `test_cleanup_error_handling` - Errors don't crash cleanup

**Acceptance Criteria**:
- [ ] All 3 tests pass
- [ ] Manipulates timestamps to simulate staleness
- [ ] Verifies resource cleanup

**Traceability**: FR-3, NFR-3, NFR-6

---

### Task 3.4: Integration Tests - Tool Actions

**File**: `tests/integration/test_browser_tools.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Phase 2 complete  
**Priority**: MUST HAVE

**Description**: Test all pos_browser actions end-to-end

**Test Cases**:
- `test_navigate_success` - Navigate to real URL
- `test_navigate_timeout` - Timeout handling
- `test_emulate_dark_mode` - Set color scheme
- `test_screenshot_to_file` - Save screenshot
- `test_screenshot_base64` - Base64 mode
- `test_set_viewport` - Viewport resizing
- `test_close_session` - Explicit close
- `test_unknown_action` - Error handling

**Acceptance Criteria**:
- [ ] All 8 tests pass
- [ ] Uses real Playwright (headless Chromium)
- [ ] Cleans up after each test
- [ ] Screenshots verified (file exists, size > 0)

**Traceability**: FR-4 through FR-10, NFR-6, NFR-7

---

### Task 3.5: Integration Test - Multi-Chat Isolation

**File**: `tests/integration/test_browser_tools.py`  
**Estimated Time**: 45 minutes  
**Dependencies**: Task 3.4  
**Priority**: MUST HAVE

**Description**: Test concurrent sessions don't interfere

**Test Case**: `test_concurrent_sessions_isolated`

**Scenario**:
1. Create session "chat-A", navigate to /page1
2. Create session "chat-B", navigate to /page2
3. Verify chat-A still on /page1
4. Verify chat-B on /page2
5. Close both sessions

**Acceptance Criteria**:
- [ ] Test passes
- [ ] Uses asyncio.gather for concurrency
- [ ] Verifies no state leakage

**Traceability**: FR-2, NFR-5

---

### Task 3.6: Integration Test - Full Workflow

**File**: `tests/integration/test_browser_tools.py`  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 3.4  
**Priority**: SHOULD HAVE

**Description**: Test complete docs testing workflow

**Test Case**: `test_docs_dark_mode_workflow`

**Scenario**:
1. Navigate to http://localhost:3000
2. Emulate dark mode
3. Screenshot to /tmp/dark.png
4. Emulate light mode
5. Screenshot to /tmp/light.png
6. Close session
7. Verify both files exist

**Acceptance Criteria**:
- [ ] Test passes (if docs server running)
- [ ] Otherwise skips with message
- [ ] Screenshots differ (dark vs light)

**Traceability**: User Story 2.1 (docs testing)

---

### Task 3.7: Integration Test - Element Interaction Actions

**File**: `tests/integration/test_browser_interaction.py`  
**Estimated Time**: 2 hours  
**Dependencies**: Phase 2 complete  
**Priority**: MUST HAVE

**Description**: Test click, type, fill, select actions

**Test Cases**:
- `test_click_action` - Click button, verify state change
- `test_click_right_button` - Right-click context menu
- `test_click_double` - Double-click
- `test_click_with_modifiers` - Ctrl+Click
- `test_type_action` - Keyboard typing
- `test_type_with_delay` - Human-like typing
- `test_fill_input` - Fill text input
- `test_fill_textarea` - Fill textarea
- `test_fill_not_fillable_error` - Error on div
- `test_select_by_value` - Select option by value
- `test_select_by_label` - Select option by label
- `test_select_by_index` - Select option by index
- `test_select_not_select_error` - Error on non-select

**Acceptance Criteria**:
- [ ] All 13 tests pass
- [ ] Uses test HTML page with form elements
- [ ] Verifies DOM state changes
- [ ] Error cases tested

**Traceability**: FR-9, FR-10, FR-11, FR-12

---

### Task 3.8: Integration Test - Waiting and Querying Actions

**File**: `tests/integration/test_browser_waiting.py`  
**Estimated Time**: 1.5 hours  
**Dependencies**: Phase 2 complete  
**Priority**: MUST HAVE

**Description**: Test wait and query actions

**Test Cases**:
- `test_wait_for_visible` - Element appears
- `test_wait_for_hidden` - Element disappears
- `test_wait_for_attached` - Element added to DOM
- `test_wait_for_detached` - Element removed from DOM
- `test_wait_timeout` - Timeout error
- `test_query_text` - Get text content
- `test_query_value` - Get input value
- `test_query_attributes` - Get href, class, etc.
- `test_query_visibility` - Check visible/hidden
- `test_query_state` - Check enabled/checked
- `test_query_multiple_properties` - Batch query

**Acceptance Criteria**:
- [ ] All 11 tests pass
- [ ] Uses JavaScript to manipulate DOM dynamically
- [ ] Verifies timing behavior
- [ ] Property extraction accurate

**Traceability**: FR-13, FR-14

---

### Task 3.9: Integration Test - JavaScript and State Actions

**File**: `tests/integration/test_browser_state.py`  
**Estimated Time**: 1 hour  
**Dependencies**: Phase 2 complete  
**Priority**: MUST HAVE

**Description**: Test evaluate, cookies, local storage actions

**Test Cases**:
- `test_evaluate_simple` - Evaluate document.title
- `test_evaluate_with_args` - Pass arguments
- `test_evaluate_error` - JavaScript error handling
- `test_get_cookies` - Retrieve cookies
- `test_set_cookies` - Set cookies
- `test_cookie_persistence` - Cookies persist in session
- `test_get_local_storage` - Retrieve local storage
- `test_local_storage_manipulation` - Set via evaluate, read via get

**Acceptance Criteria**:
- [ ] All 8 tests pass
- [ ] Verifies data round-trip
- [ ] Error handling tested

**Traceability**: FR-5, FR-8

---

**Phase 3 Deliverables**:
- `tests/unit/test_browser_manager.py` (6 tests - per-session architecture)
- `tests/integration/test_browser_tools.py` (10 tests - basic actions)
- `tests/integration/test_browser_interaction.py` (13 tests - click/type/fill/select)
- `tests/integration/test_browser_waiting.py` (11 tests - wait/query)
- `tests/integration/test_browser_state.py` (8 tests - evaluate/cookies/storage)
- **Total: 48 tests**
- >80% code coverage

**Phase 3 Validation Gate**:
- [ ] All 48 tests pass (`pytest tests/`)
- [ ] Coverage >80% (`pytest --cov`)
- [ ] All action handlers tested
- [ ] Per-session isolation verified
- [ ] Error cases covered
- [ ] No linter errors (`ruff check`)
- [ ] All docstrings present
- [ ] Concurrency analysis documented

---

## Phase 4: Documentation & Deployment (1-2 hours)

**Goal**: Production-ready documentation and configuration

### Task 4.1: Add Playwright Dependency

**File**: `mcp_server/requirements.txt`  
**Estimated Time**: 5 minutes  
**Dependencies**: None  
**Priority**: MUST HAVE

**Description**: Add Playwright to dependencies

**Acceptance Criteria**:
- [ ] Add line: `playwright>=1.40.0`
- [ ] Verify installs: `pip install -r mcp_server/requirements.txt`

**Traceability**: NFR-10

---

### Task 4.2: Create Installation Guide

**File**: `mcp_server/README.md` (append section)  
**Estimated Time**: 30 minutes  
**Dependencies**: Task 4.1  
**Priority**: MUST HAVE

**Description**: Document installation and setup

**Content**:
- Playwright installation steps
- Chromium download (playwright install chromium)
- Config changes (enabled_tool_groups)
- Auto-approve list update

**Acceptance Criteria**:
- [ ] Section added to README
- [ ] Commands are copy-pasteable
- [ ] Covers all setup steps

**Traceability**: NFR-8

---

### Task 4.3: Document pos_browser Usage

**File**: `docs/content/browser-tools.md` (new)  
**Estimated Time**: 45 minutes  
**Dependencies**: Phase 2 complete  
**Priority**: MUST HAVE

**Description**: User-facing documentation for pos_browser

**Content**:
- Overview and use cases
- Parameter reference (all actions)
- Examples (navigate, dark mode, screenshot)
- Session management explanation
- Error handling tips

**Acceptance Criteria**:
- [ ] Markdown file created
- [ ] Examples are tested and working
- [ ] Linked from main docs index

**Traceability**: NFR-8

---

### Task 4.4: Update Auto-Approve Config

**File**: `.cursor/mcp.json`  
**Estimated Time**: 5 minutes  
**Dependencies**: Phase 2 complete  
**Priority**: SHOULD HAVE

**Description**: Add pos_browser to auto-approve list

**Acceptance Criteria**:
- [ ] Add "pos_browser" to autoApprove array
- [ ] Verify Cursor doesn't prompt for approval

**Traceability**: User Experience Success

---

### Task 4.5: Create Concurrency Analysis Doc

**File**: `mcp_server/CONCURRENCY_ANALYSIS.md`  
**Estimated Time**: 30 minutes  
**Dependencies**: Phase 1 complete  
**Priority**: MUST HAVE

**Description**: Document shared state and protection mechanisms

**Content**:
- Shared state: `_sessions` dict
- Protection: asyncio.Lock
- Race conditions: None (lock guards all access)
- Deadlocks: None (single lock, no nesting)
- Testing: Unit tests verify

**Acceptance Criteria**:
- [ ] Document created
- [ ] Follows production code checklist format
- [ ] References locking-strategies.md

**Traceability**: NFR-4, NFR-8

---

### Task 4.6: Production Code Checklist Review

**File**: All implementation files  
**Estimated Time**: 30 minutes  
**Dependencies**: Phases 1-3 complete  
**Priority**: MUST HAVE

**Description**: Verify all code meets production standards

**Checklist**:
- [ ] All functions have Sphinx docstrings
- [ ] All parameters have type hints
- [ ] Concurrency analysis documented
- [ ] No hardcoded secrets/paths
- [ ] Error messages have remediation
- [ ] Logging at appropriate levels
- [ ] No linter errors

**Acceptance Criteria**:
- [ ] All checklist items pass
- [ ] Document deviations if any

**Traceability**: NFR-8

---

**Phase 4 Deliverables**:
- Updated `mcp_server/requirements.txt`
- Updated `mcp_server/README.md`
- New `docs/content/browser-tools.md` (comprehensive action reference)
- Updated `.cursor/mcp.json`
- New `mcp_server/CONCURRENCY_ANALYSIS.md`
- Production code checklist completed

**Phase 4 Validation Gate**:
- [ ] All documentation complete (covers 20+ actions)
- [ ] Installation tested end-to-end
- [ ] Auto-approve working
- [ ] Production checklist 100% pass
- [ ] Ready for deployment

---

## Phase 5: Advanced Features (15-20 hours)

**Goal**: Implement Phase 2 implementation scope features

**Note**: These are in-scope, implemented after Phase 1-4 core features are stable. All 28 FRs will be implemented during spec execution.

### Task 5.1: Implement Test Script Execution (FR-19)

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 3 hours  
**Priority**: SHOULD HAVE

**Description**: Execute Playwright test scripts (.spec.ts/.spec.js)

**Acceptance Criteria**:
- [ ] Action: `run_test`
- [ ] Parameters: `test_file`, `config` (optional)
- [ ] Executes via `pytest` or `npx playwright test`
- [ ] Captures test results, screenshots, traces
- [ ] Returns pass/fail, errors, execution time
- [ ] Supports headless and headful modes

**Use Case**: Testing contractor workflow

**Traceability**: FR-19

---

### Task 5.2: Implement Network Interception (FR-20)

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 4 hours  
**Priority**: SHOULD HAVE

**Description**: Intercept and modify network requests/responses

**Acceptance Criteria**:
- [ ] Action: `intercept_network`
- [ ] Parameters: `pattern`, `response_override`, `block`
- [ ] Uses `page.route(pattern, handler)`
- [ ] Can mock API responses
- [ ] Can block resources (images, CSS)
- [ ] Can modify headers, status codes
- [ ] Returns interception stats

**Use Case**: Testing without backend, performance optimization

**Traceability**: FR-20

---

### Task 5.3: Implement Tab Management (FR-21)

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 3 hours  
**Priority**: SHOULD HAVE

**Description**: Manage multiple tabs within session

**Acceptance Criteria**:
- [ ] Actions: `new_tab`, `switch_tab`, `close_tab`, `list_tabs`
- [ ] Tracks multiple pages per session
- [ ] Tab isolation (cookies shared, DOM isolated)
- [ ] Returns tab IDs
- [ ] Session cleanup closes all tabs

**Use Case**: Multi-page workflows

**Traceability**: FR-21

---

### Task 5.4: Implement File I/O (FR-22)

**File**: `mcp_server/server/tools/browser_tools.py`  
**Estimated Time**: 2 hours  
**Priority**: SHOULD HAVE

**Description**: File uploads and downloads

**Acceptance Criteria**:
- [ ] Action: `upload_file` (selector, file_path)
- [ ] Action: `download_file` (trigger_selector, save_path)
- [ ] Uses `page.set_input_files()` for uploads
- [ ] Uses `page.expect_download()` for downloads
- [ ] Handles download timeouts
- [ ] Returns file paths, sizes

**Use Case**: Form testing, document generation

**Traceability**: FR-22

---

### Task 5.5: Implement Cross-Browser Support (FR-23)

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 2 hours  
**Priority**: NICE TO HAVE

**Description**: Support Firefox, WebKit, Chromium

**Acceptance Criteria**:
- [ ] Parameter: `browser` (chromium, firefox, webkit)
- [ ] Launches correct browser type
- [ ] Per-session browser type (can mix in same manager)
- [ ] Returns browser type in session info
- [ ] Installation docs for all browsers

**Use Case**: Cross-browser testing

**Traceability**: FR-23

---

### Task 5.6: Implement Headful Mode (FR-24)

**File**: `mcp_server/browser_manager.py`  
**Estimated Time**: 1 hour  
**Priority**: NICE TO HAVE

**Description**: Visual debugging mode

**Acceptance Criteria**:
- [ ] Parameter: `headless` (default: True)
- [ ] Launches visible browser when False
- [ ] Warning about performance impact
- [ ] Returns headless status in session info

**Use Case**: Debugging, demos

**Traceability**: FR-24

---

**Phase 5 Deliverables**:
- Test script execution capability
- Network interception and mocking
- Multi-tab management
- File upload/download
- Cross-browser support (Chromium, Firefox, WebKit)
- Headful mode for visual debugging

**Phase 5 Validation Gate**:
- [ ] All 6 advanced features implemented
- [ ] Comprehensive tests for each feature
- [ ] Documentation updated
- [ ] Testing contractor use case validated
- [ ] Performance benchmarks acceptable

---

## Dependency Graph

```
Phase 1 (Core)
├─> Task 1.1 (BrowserSession)
├─> Task 1.2 (BrowserManager) [depends: 1.1]
├─> Task 1.3 (initialize) [depends: 1.2]
├─> Task 1.4 (get_session) [depends: 1.3]
├─> Task 1.5 (cleanup) [depends: 1.4]
├─> Task 1.6 (close_session) [depends: 1.4]
└─> Task 1.7 (shutdown) [depends: 1.6]
       ↓
Phase 2 (Integration)
├─> Task 2.1 (skeleton) [depends: Phase 1]
├─> Task 2.2-2.6 (actions) [depends: 2.1]
├─> Task 2.7 (factory) [depends: 2.1]
└─> Task 2.8 (registration) [depends: 2.7]
       ↓
Phase 3 (Testing)
├─> Task 3.1-3.3 (unit tests) [depends: Phase 1]
└─> Task 3.4-3.6 (integration tests) [depends: Phase 2]
       ↓
Phase 4 (Docs)
└─> Task 4.1-4.6 (all parallel) [depends: Phases 1-3]
```

---

## Risk Mitigation

### High Risk Items

**Risk 1**: Playwright not installed  
**Mitigation**: Clear install docs, error message with remediation  
**Fallback**: Disable browser tool group

**Risk 2**: Zombie browser processes  
**Mitigation**: Auto-cleanup (1hr timeout), explicit shutdown on server stop  
**Monitoring**: Log active session count

**Risk 3**: Concurrent access bugs  
**Mitigation**: Comprehensive unit tests, asyncio.Lock protection  
**Validation**: test_concurrent_get_session

---

## Success Criteria Summary

**Functional**:
- [ ] All 6 actions (navigate, emulate, screenshot, viewport, console, close) work
- [ ] Multi-session isolation verified
- [ ] Tool count = 9 (under 20 limit)
- [ ] Can test docs in dark mode in <5 tool calls

**Quality**:
- [ ] 22 tests pass (12 unit + 10 integration)
- [ ] >80% code coverage
- [ ] All docstrings present (Sphinx)
- [ ] Concurrency analysis documented
- [ ] No linter errors

**Deployment**:
- [ ] Installation docs complete
- [ ] Auto-approve configured
- [ ] Production checklist 100%
- [ ] Ready to merge

---

**Phase 3 Complete** - Ready for Phase 4 (Implementation Guidance)

