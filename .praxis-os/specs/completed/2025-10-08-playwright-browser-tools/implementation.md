# Implementation Guidance
# Browser Automation Tool for Agent OS MCP Server

**Version**: 1.0  
**Date**: October 8, 2025  
**Requirements**: See `srd.md`  
**Design**: See `specs.md`  
**Tasks**: See `tasks.md`  
**Phase**: 4 of 6 (spec_creation_v1)

---

## 1. Overview

This document provides concrete implementation patterns, code examples, and troubleshooting guidance for building the browser automation tool. Follow these patterns to ensure consistency with Agent OS standards.

---

## 2. Core Patterns

### 2.1 Simplified Architecture Pattern

**ARCHITECTURE CHANGE**: Per-session browsers (not shared)

```python
from playwright.async_api import async_playwright

class BrowserManager:
    """
    Manager for per-session browser processes.
    
    ARCHITECTURE: Each session gets its own Playwright + browser process.
    No shared browser state = simpler code, better isolation.
    
    :param session_timeout: Idle timeout in seconds (default: 3600)
    """
    
    def __init__(self, session_timeout: int = 3600):
        """Initialize manager (no browser launched yet - lazy per session)."""
        self._sessions: Dict[str, BrowserSession] = {}
        self._lock = asyncio.Lock()  # Only protects session dict
        self._session_timeout = session_timeout
        # NO shared _playwright or _browser! Each session has its own.
```

**Key Points**:
- ✅ No shared browser process to manage
- ✅ Lock only protects session dict (not browser state)
- ✅ Each session fully independent
- ✅ Simpler than singleton approach
- ✅ Better fault isolation (crash doesn't affect other sessions)

---

### 2.2 Session Isolation Pattern

**Use For**: Multi-session management

```python
from dataclasses import dataclass, field
import time

@dataclass
class BrowserSession:
    """
    Fully isolated browser session (one browser process per session).
    
    ARCHITECTURE: Per-session browser (not shared)
    - Each session has its own Playwright + Chromium process
    - Simpler cleanup (kill process)
    - Better fault isolation (crash doesn't affect other sessions)
    - Developer experience > memory efficiency
    """
    playwright: Any  # Playwright instance (per session)
    browser: Browser  # Chromium process (per session)
    page: Page  # Page within browser
    created_at: float
    last_access: float = field(default_factory=time.time)
    
    async def cleanup(self):
        """Release resources (kill browser process)."""
        try:
            await self.page.close()
            await self.browser.close()
            await self.playwright.stop()  # Stop this session's Playwright
        except Exception as e:
            logger.warning(f"Session cleanup error: {e}")
            # Don't raise - cleanup is best-effort


class BrowserManager:
    async def get_session(self, session_id: str = "default") -> BrowserSession:
        """
        Get or create fully isolated session (thread-safe).
        
        ARCHITECTURE: Each session gets its own browser process.
        No shared browser to manage - much simpler!
        """
        async with self._lock:
            # Cleanup stale sessions first
            await self._cleanup_stale_sessions()
            
            # Reuse existing session
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session.last_access = time.time()
                logger.debug(f"Session reused: {session_id}")
                return session
            
            # Create NEW browser process for this session
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage']
            )
            page = await browser.new_page()
            
            session = BrowserSession(
                playwright=playwright,  # This session's Playwright
                browser=browser,  # This session's browser process
                page=page,
                created_at=time.time()
            )
            self._sessions[session_id] = session
            logger.info(f"Session created: {session_id} with new browser process (total sessions: {len(self._sessions)})")
            return session
```

**Key Points**:
- ✅ Lock guards all dict access (thread-safe)
- ✅ Auto-cleanup before creating new sessions
- ✅ Updates last_access for existing sessions
- ✅ Logs session count for monitoring

---

### 2.3 Stale Session Cleanup Pattern

**Use For**: Preventing resource leaks

```python
class BrowserManager:
    async def _cleanup_stale_sessions(self):
        """Remove sessions idle beyond timeout (private)."""
        now = time.time()
        stale_ids = [
            sid for sid, session in self._sessions.items()
            if (now - session.last_access) > self._session_timeout
        ]
        
        for sid in stale_ids:
            try:
                session = self._sessions.pop(sid)
                await session.cleanup()
                logger.info(f"Cleaned up stale session: {sid} (idle for {now - session.last_access:.0f}s)")
            except Exception as e:
                logger.error(f"Error cleaning up session {sid}: {e}", exc_info=True)
                # Continue - don't let one failure block others
```

**Key Points**:
- ✅ List comprehension to identify stale sessions
- ✅ Cleanup errors don't abort loop
- ✅ Logs idle time for debugging
- ✅ Private method (implementation detail)

---

### 2.4 Action Dispatch Pattern

**Use For**: Consolidated tool with multiple actions

```python
@mcp.tool()
async def pos_browser(
    action: str,
    session_id: Optional[str] = None,
    url: Optional[str] = None,
    color_scheme: Optional[str] = None,
    screenshot_path: Optional[str] = None,
    screenshot_full_page: bool = False,
    viewport_width: Optional[int] = None,
    viewport_height: Optional[int] = None,
    timeout: int = 30000,
    wait_until: str = "load",
) -> Dict[str, Any]:
    """
    Browser automation with session isolation.
    
    Actions: navigate, emulate_media, screenshot, set_viewport, get_console, close
    
    Examples:
        >>> pos_browser(action="navigate", url="https://example.com", session_id="test-1")
        >>> pos_browser(action="emulate_media", color_scheme="dark", session_id="test-1")
        >>> pos_browser(action="screenshot", screenshot_path="/tmp/dark.png", session_id="test-1")
        >>> pos_browser(action="close", session_id="test-1")
    """
    try:
        sid = session_id or "default"
        
        # Close doesn't need session (explicit cleanup)
        if action == "close":
            await browser_manager.close_session(sid)
            return {"status": "success", "action": "close", "session_id": sid}
        
        # All other actions need session
        session = await browser_manager.get_session(sid)
        page = session.page
        
        # Dispatch to action handlers
        if action == "navigate":
            return await _handle_navigate(page, sid, url, timeout, wait_until)
        elif action == "emulate_media":
            return await _handle_emulate_media(page, sid, color_scheme)
        elif action == "screenshot":
            return await _handle_screenshot(page, sid, screenshot_path, screenshot_full_page)
        elif action == "set_viewport":
            return await _handle_set_viewport(page, sid, viewport_width, viewport_height)
        elif action == "get_console":
            return await _handle_get_console(page, sid)
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}",
                "valid_actions": ["navigate", "emulate_media", "screenshot", "set_viewport", "get_console", "close"]
            }
    
    except Exception as e:
        logger.error(f"pos_browser({action}) failed: {e}", exc_info=True)
        return {
            "status": "error",
            "action": action,
            "session_id": sid,
            "error": str(e),
            "remediation": "Check parameters and ensure browser is initialized"
        }
```

**Key Points**:
- ✅ Single entry point for all actions
- ✅ Action handlers are separate functions (separation of concerns)
- ✅ Top-level try/catch for safety
- ✅ Error responses include remediation

---

## 3. Action Handler Implementations

### 3.1 Navigate Handler

```python
async def _handle_navigate(
    page: Page,
    session_id: str,
    url: Optional[str],
    timeout: int,
    wait_until: str
) -> Dict[str, Any]:
    """Navigate to URL with configurable wait."""
    if not url:
        return {
            "status": "error",
            "error": "url parameter required for navigate action",
            "remediation": "Provide url parameter"
        }
    
    try:
        logger.debug(f"Navigate ({session_id}): {url}")
        response = await page.goto(url, timeout=timeout, wait_until=wait_until)
        title = await page.title()
        
        return {
            "status": "success",
            "action": "navigate",
            "session_id": session_id,
            "url": page.url,  # Final URL (after redirects)
            "title": title,
            "http_status": response.status if response else None
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "navigate",
            "session_id": session_id,
            "error": f"Navigation timeout ({timeout}ms)",
            "url": url,
            "remediation": "Increase timeout parameter or check network connectivity"
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "navigate",
            "session_id": session_id,
            "error": str(e),
            "url": url
        }
```

**Key Points**:
- ✅ Validates required parameters
- ✅ Specific TimeoutError handling
- ✅ Returns final URL (handles redirects)
- ✅ HTTP status included

---

### 3.2 Emulate Media Handler

```python
async def _handle_emulate_media(
    page: Page,
    session_id: str,
    color_scheme: Optional[str] = None,
    reduced_motion: Optional[str] = None
) -> Dict[str, Any]:
    """Emulate media features (dark mode, reduced motion)."""
    try:
        # Build emulate_media params
        params = {}
        if color_scheme:
            params["color_scheme"] = color_scheme  # "light", "dark", "no-preference"
        if reduced_motion:
            params["reduced_motion"] = reduced_motion  # "reduce", "no-preference"
        
        logger.debug(f"Emulate media ({session_id}): {params}")
        await page.emulate_media(**params)
        
        return {
            "status": "success",
            "action": "emulate_media",
            "session_id": session_id,
            "applied": params
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "emulate_media",
            "session_id": session_id,
            "error": str(e),
            "remediation": "Valid color_scheme: light|dark|no-preference. Valid reduced_motion: reduce|no-preference"
        }
```

**Key Points**:
- ✅ Optional parameters (can set one or both)
- ✅ Documents valid values in remediation
- ✅ Returns applied configuration

---

### 3.3 Screenshot Handler

```python
from pathlib import Path

async def _handle_screenshot(
    page: Page,
    session_id: str,
    screenshot_path: Optional[str],
    screenshot_full_page: bool
) -> Dict[str, Any]:
    """Capture page screenshot."""
    try:
        # Validate path if provided (security)
        if screenshot_path:
            path = Path(screenshot_path).resolve()
            workspace = Path.cwd()
            tmp = Path("/tmp")
            
            # Must be in workspace or /tmp
            if not (str(path).startswith(str(workspace)) or str(path).startswith(str(tmp))):
                return {
                    "status": "error",
                    "action": "screenshot",
                    "session_id": session_id,
                    "error": "screenshot_path must be in workspace or /tmp",
                    "remediation": f"Use path under {workspace} or /tmp"
                }
            
            # Create parent dir if needed
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Capture screenshot
        logger.debug(f"Screenshot ({session_id}): full_page={screenshot_full_page}, path={screenshot_path}")
        screenshot_bytes = await page.screenshot(
            full_page=screenshot_full_page,
            path=screenshot_path,
            type="png"
        )
        
        result = {
            "status": "success",
            "action": "screenshot",
            "session_id": session_id,
            "full_page": screenshot_full_page
        }
        
        if screenshot_path:
            result["path"] = str(path)
            result["size_bytes"] = len(screenshot_bytes)
            logger.info(f"Screenshot saved: {path} ({len(screenshot_bytes)} bytes)")
        else:
            # Base64 encode for return
            import base64
            result["base64"] = base64.b64encode(screenshot_bytes).decode()
        
        return result
    
    except Exception as e:
        return {
            "status": "error",
            "action": "screenshot",
            "session_id": session_id,
            "error": str(e)
        }
```

**Key Points**:
- ✅ Path validation (security)
- ✅ Creates parent directories
- ✅ Base64 fallback if no path
- ✅ Returns file size for monitoring

---

### 3.4 Viewport Handler

```python
async def _handle_set_viewport(
    page: Page,
    session_id: str,
    width: Optional[int],
    height: Optional[int]
) -> Dict[str, Any]:
    """Set browser viewport dimensions."""
    if not width or not height:
        return {
            "status": "error",
            "action": "set_viewport",
            "error": "Both viewport_width and viewport_height required",
            "remediation": "Provide both width and height in pixels"
        }
    
    try:
        logger.debug(f"Set viewport ({session_id}): {width}x{height}")
        await page.set_viewport_size({"width": width, "height": height})
        
        return {
            "status": "success",
            "action": "set_viewport",
            "session_id": session_id,
            "viewport": {"width": width, "height": height}
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "set_viewport",
            "session_id": session_id,
            "error": str(e)
        }
```

**Key Points**:
- ✅ Validates both params required
- ✅ Returns applied viewport
- ✅ Simple and straightforward

---

### 3.5 Console Handler (Stub)

```python
async def _handle_get_console(
    page: Page,
    session_id: str
) -> Dict[str, Any]:
    """Get console messages (stub for v1)."""
    return {
        "status": "success",
        "action": "get_console",
        "session_id": session_id,
        "console_messages": [],
        "note": "Console capture not implemented in v1. Use browser DevTools for console inspection."
    }
```

**Key Points**:
- ✅ Stub implementation (documents limitation)
- ✅ Returns success (doesn't break workflows)
- ✅ Note explains how to get console messages

---

### 3.6 Click Handler

```python
async def _handle_click(
    page: Page,
    session_id: str,
    selector: Optional[str],
    button: str = "left",
    click_count: int = 1,
    modifiers: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Click element with selector."""
    if not selector:
        return {
            "status": "error",
            "error": "selector parameter required for click action",
            "remediation": "Provide CSS selector (e.g., 'button#submit')"
        }
    
    try:
        logger.debug(f"Click ({session_id}): {selector} (button={button}, count={click_count})")
        
        await page.click(
            selector,
            button=button,
            click_count=click_count,
            modifiers=modifiers or [],
            timeout=30000
        )
        
        return {
            "status": "success",
            "action": "click",
            "session_id": session_id,
            "selector": selector,
            "button": button,
            "click_count": click_count
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "click",
            "session_id": session_id,
            "error": f"Element not found or not clickable: {selector}",
            "remediation": "Check selector is correct. Use query action to verify element exists."
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "click",
            "session_id": session_id,
            "error": str(e),
            "selector": selector
        }
```

**Key Points**:
- ✅ Supports button (left, right, middle)
- ✅ Supports click_count (double-click, triple-click)
- ✅ Supports modifiers (Shift, Control, Alt, Meta)
- ✅ Clear remediation for element not found

---

### 3.7 Type Handler

```python
async def _handle_type(
    page: Page,
    session_id: str,
    text: Optional[str],
    delay: int = 0
) -> Dict[str, Any]:
    """Type text with keyboard."""
    if not text:
        return {
            "status": "error",
            "error": "text parameter required for type action",
            "remediation": "Provide text to type"
        }
    
    try:
        logger.debug(f"Type ({session_id}): {len(text)} chars (delay={delay}ms)")
        
        await page.keyboard.type(text, delay=delay)
        
        return {
            "status": "success",
            "action": "type",
            "session_id": session_id,
            "characters_typed": len(text),
            "delay": delay
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "type",
            "session_id": session_id,
            "error": str(e)
        }
```

**Key Points**:
- ✅ delay parameter for human-like typing
- ✅ Returns character count
- ✅ Types into currently focused element

---

### 3.8 Fill Handler

```python
async def _handle_fill(
    page: Page,
    session_id: str,
    selector: Optional[str],
    value: Optional[str],
    force: bool = False
) -> Dict[str, Any]:
    """Fill form field."""
    if not selector:
        return {
            "status": "error",
            "error": "selector parameter required for fill action",
            "remediation": "Provide CSS selector for input/textarea"
        }
    if value is None:
        value = ""  # Allow clearing field
    
    try:
        logger.debug(f"Fill ({session_id}): {selector} ({len(value)} chars)")
        
        await page.fill(selector, value, force=force, timeout=30000)
        
        # Get element type for context
        element_type = await page.evaluate(
            f"document.querySelector({repr(selector)})?.tagName"
        )
        
        return {
            "status": "success",
            "action": "fill",
            "session_id": session_id,
            "selector": selector,
            "value_length": len(value),
            "element_type": element_type
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "fill",
            "session_id": session_id,
            "error": f"Element not found: {selector}",
            "remediation": "Check selector is correct. Use query action to verify element exists."
        }
    except Exception as e:
        error_msg = str(e)
        if "not fillable" in error_msg.lower():
            return {
                "status": "error",
                "action": "fill",
                "session_id": session_id,
                "error": f"Element is not fillable: {selector}",
                "remediation": "fill only works on input/textarea/contenteditable. Use type for other elements."
            }
        return {
            "status": "error",
            "action": "fill",
            "session_id": session_id,
            "error": error_msg,
            "selector": selector
        }
```

**Key Points**:
- ✅ Clears existing value before filling
- ✅ force parameter to bypass actionability checks
- ✅ Specific error for non-fillable elements
- ✅ Returns element type for context

---

### 3.9 Select Handler

```python
async def _handle_select(
    page: Page,
    session_id: str,
    selector: Optional[str],
    value: Optional[str] = None,
    label: Optional[str] = None,
    index: Optional[int] = None
) -> Dict[str, Any]:
    """Select dropdown option."""
    if not selector:
        return {
            "status": "error",
            "error": "selector parameter required for select action",
            "remediation": "Provide CSS selector for <select> element"
        }
    if not any([value, label, index is not None]):
        return {
            "status": "error",
            "error": "Must provide one of: value, label, or index",
            "remediation": "Specify which option to select"
        }
    
    try:
        logger.debug(f"Select ({session_id}): {selector} (value={value}, label={label}, index={index})")
        
        # Build select_option params
        option = {}
        if value:
            option = {"value": value}
        elif label:
            option = {"label": label}
        elif index is not None:
            option = {"index": index}
        
        selected_values = await page.select_option(selector, option, timeout=30000)
        
        return {
            "status": "success",
            "action": "select",
            "session_id": session_id,
            "selector": selector,
            "selected_values": selected_values
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "select",
            "session_id": session_id,
            "error": f"Element not found: {selector}",
            "remediation": "Check selector is correct and targets <select> element."
        }
    except Exception as e:
        error_msg = str(e)
        if "not a select" in error_msg.lower():
            return {
                "status": "error",
                "action": "select",
                "session_id": session_id,
                "error": f"Element is not <select>: {selector}",
                "remediation": "select only works on <select> elements. For other inputs, use click or fill."
            }
        return {
            "status": "error",
            "action": "select",
            "session_id": session_id,
            "error": error_msg,
            "selector": selector
        }
```

**Key Points**:
- ✅ Three selection methods (value, label, index)
- ✅ Validates at least one method provided
- ✅ Returns selected values (supports multi-select)
- ✅ Specific error for non-select elements

---

### 3.10 Wait Handler

```python
async def _handle_wait(
    page: Page,
    session_id: str,
    selector: Optional[str],
    wait_for: str = "visible",
    timeout: int = 30000
) -> Dict[str, Any]:
    """Wait for element state."""
    if not selector:
        return {
            "status": "error",
            "error": "selector parameter required for wait action",
            "remediation": "Provide CSS selector to wait for"
        }
    
    valid_states = ["visible", "hidden", "attached", "detached"]
    if wait_for not in valid_states:
        return {
            "status": "error",
            "error": f"Invalid wait_for: {wait_for}",
            "remediation": f"Must be one of: {', '.join(valid_states)}"
        }
    
    try:
        start_time = asyncio.get_event_loop().time()
        logger.debug(f"Wait ({session_id}): {selector} {wait_for} (timeout={timeout}ms)")
        
        await page.wait_for_selector(selector, state=wait_for, timeout=timeout)
        
        duration_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        return {
            "status": "success",
            "action": "wait",
            "session_id": session_id,
            "selector": selector,
            "wait_for": wait_for,
            "duration_ms": duration_ms
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "wait",
            "session_id": session_id,
            "error": f"Timeout waiting for {selector} to be {wait_for}",
            "timeout": timeout,
            "remediation": "Increase timeout or check if element state changes as expected."
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "wait",
            "session_id": session_id,
            "error": str(e),
            "selector": selector
        }
```

**Key Points**:
- ✅ Four wait strategies (visible, hidden, attached, detached)
- ✅ Validates wait_for parameter
- ✅ Returns actual wait duration
- ✅ Configurable timeout

---

### 3.11 Query Handler

```python
async def _handle_query(
    page: Page,
    session_id: str,
    selector: Optional[str],
    properties: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Query element properties."""
    if not selector:
        return {
            "status": "error",
            "error": "selector parameter required for query action",
            "remediation": "Provide CSS selector to query"
        }
    
    properties = properties or ["text", "visible"]
    
    try:
        logger.debug(f"Query ({session_id}): {selector} ({len(properties)} properties)")
        
        # Wait for element
        element = await page.wait_for_selector(selector, state="attached", timeout=30000)
        if not element:
            return {
                "status": "error",
                "action": "query",
                "session_id": session_id,
                "error": f"Element not found: {selector}",
                "remediation": "Check selector is correct."
            }
        
        # Query properties
        result_props = {}
        for prop in properties:
            if prop == "text":
                result_props["text"] = await element.text_content()
            elif prop == "value":
                result_props["value"] = await element.input_value()
            elif prop == "visible":
                result_props["visible"] = await element.is_visible()
            elif prop == "enabled":
                result_props["enabled"] = await element.is_enabled()
            elif prop == "checked":
                result_props["checked"] = await element.is_checked()
            elif prop.startswith("attribute."):
                attr_name = prop.split(".", 1)[1]
                result_props[attr_name] = await element.get_attribute(attr_name)
        
        return {
            "status": "success",
            "action": "query",
            "session_id": session_id,
            "selector": selector,
            "properties": result_props
        }
    
    except TimeoutError:
        return {
            "status": "error",
            "action": "query",
            "session_id": session_id,
            "error": f"Element not found: {selector}",
            "remediation": "Check selector is correct."
        }
    except Exception as e:
        return {
            "status": "error",
            "action": "query",
            "session_id": session_id,
            "error": str(e),
            "selector": selector
        }
```

**Key Points**:
- ✅ Batch property querying
- ✅ Supports text, value, visible, enabled, checked
- ✅ Supports arbitrary attributes (attribute.href, attribute.class)
- ✅ Default to text + visible if not specified

---

### 3.12 Evaluate Handler

```python
async def _handle_evaluate(
    page: Page,
    session_id: str,
    script: Optional[str],
    args: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """Execute JavaScript in page context."""
    if not script:
        return {
            "status": "error",
            "error": "script parameter required for evaluate action",
            "remediation": "Provide JavaScript code to execute"
        }
    
    try:
        logger.debug(f"Evaluate ({session_id}): {len(script)} chars")
        
        result = await page.evaluate(script, *(args or []))
        
        return {
            "status": "success",
            "action": "evaluate",
            "session_id": session_id,
            "result": result
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "evaluate",
            "session_id": session_id,
            "error": f"JavaScript error: {str(e)}",
            "remediation": "Check JavaScript syntax and runtime errors."
        }
```

**Key Points**:
- ✅ Executes arbitrary JavaScript
- ✅ Supports passing arguments
- ✅ Returns JSON-serializable result
- ✅ **Security Note**: Trust validated in MCP layer (only AI agent calls this)

---

### 3.13 Cookies Handlers

```python
async def _handle_get_cookies(
    page: Page,
    session_id: str
) -> Dict[str, Any]:
    """Get all cookies."""
    try:
        logger.debug(f"Get cookies ({session_id})")
        
        cookies = await page.context.cookies()
        
        return {
            "status": "success",
            "action": "get_cookies",
            "session_id": session_id,
            "cookies": cookies,
            "count": len(cookies)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "get_cookies",
            "session_id": session_id,
            "error": str(e)
        }


async def _handle_set_cookies(
    page: Page,
    session_id: str,
    cookies: Optional[List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """Set cookies."""
    if not cookies:
        return {
            "status": "error",
            "error": "cookies parameter required (array of cookie dicts)",
            "remediation": "Provide list of cookies with name, value, domain/url"
        }
    
    try:
        logger.debug(f"Set cookies ({session_id}): {len(cookies)} cookies")
        
        await page.context.add_cookies(cookies)
        
        return {
            "status": "success",
            "action": "set_cookies",
            "session_id": session_id,
            "cookies_set": len(cookies)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "set_cookies",
            "session_id": session_id,
            "error": str(e),
            "remediation": "Each cookie needs: name, value, and domain or url"
        }
```

**Key Points**:
- ✅ get_cookies returns all cookies with metadata
- ✅ set_cookies validates cookie format
- ✅ Cookies persist within session

---

### 3.14 Local Storage Handler

```python
async def _handle_get_local_storage(
    page: Page,
    session_id: str
) -> Dict[str, Any]:
    """Get local storage via JavaScript."""
    try:
        logger.debug(f"Get local storage ({session_id})")
        
        # Execute JavaScript to get localStorage
        storage_entries = await page.evaluate(
            "() => Object.entries(localStorage)"
        )
        storage_dict = dict(storage_entries) if storage_entries else {}
        
        return {
            "status": "success",
            "action": "get_local_storage",
            "session_id": session_id,
            "storage": storage_dict,
            "count": len(storage_dict)
        }
    
    except Exception as e:
        return {
            "status": "error",
            "action": "get_local_storage",
            "session_id": session_id,
            "error": str(e)
        }
```

**Key Points**:
- ✅ Uses evaluate to access localStorage
- ✅ Returns dict of key-value pairs
- ✅ Can set via evaluate action

---

## 4. Dependency Injection Integration

### 4.1 ServerFactory Modification

**File**: `mcp_server/server/factory.py`

```python
from mcp_server.browser_manager import BrowserManager

class ServerFactory:
    def _create_browser_manager(self) -> BrowserManager:
        """Create browser manager for Playwright automation."""
        logger.info("Creating browser manager...")
        session_timeout = self.config.browser.get("session_timeout", 3600)
        return BrowserManager(session_timeout=session_timeout)
    
    def _create_mcp_server(
        self,
        rag_engine: RAGEngine,
        workflow_engine: WorkflowEngine,
        framework_generator: Any,
        browser_manager: BrowserManager  # ⭐ NEW
    ) -> FastMCP:
        """Create MCP server with all tools."""
        from mcp_server.server.tools import register_all_tools
        
        mcp = FastMCP("Agent OS RAG")
        
        tool_count = register_all_tools(
            mcp=mcp,
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            browser_manager=browser_manager,  # ⭐ NEW
            base_path=self.paths["base"],
            enabled_groups=self.config.mcp.get("enabled_tool_groups"),
            max_tools_warning=self.config.mcp.get("max_tools_warning", 20)
        )
        
        return mcp
    
    def create_server(self) -> FastMCP:
        """Create complete MCP server."""
        rag_engine = self._create_rag_engine()
        workflow_engine = self._create_workflow_engine()
        framework_generator = self._create_framework_generator()
        browser_manager = self._create_browser_manager()  # ⭐ NEW
        
        server = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator,
            browser_manager=browser_manager  # ⭐ NEW
        )
        
        return server
```

**Key Points**:
- ✅ Respects config (session_timeout)
- ✅ Follows existing DI pattern
- ✅ Passes through to tool registration

---

### 4.2 Tool Registration

**File**: `mcp_server/server/tools/__init__.py`

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
    """Register all MCP tools."""
    if enabled_groups is None:
        enabled_groups = ["rag", "workflow", "browser"]  # ⭐ ADD browser
    
    tool_count = 0
    
    # Existing tools...
    if "rag" in enabled_groups:
        from .rag_tools import register_rag_tools
        count = register_rag_tools(mcp, rag_engine)
        tool_count += count
        logger.info(f"✅ Registered {count} RAG tool(s)")
    
    if "workflow" in enabled_groups:
        from .workflow_tools import register_workflow_tools
        count = register_workflow_tools(mcp, workflow_engine, framework_generator, base_path)
        tool_count += count
        logger.info(f"✅ Registered {count} workflow tool(s)")
    
    # ⭐ NEW: Browser tools
    if "browser" in enabled_groups and browser_manager:
        from .browser_tools import register_browser_tools
        count = register_browser_tools(mcp, browser_manager)
        tool_count += count
        logger.info(f"✅ Registered {count} browser tool(s)")
    
    # Tool count warning
    if tool_count > max_tools_warning:
        logger.warning(
            f"⚠️  Tool count ({tool_count}) exceeds recommended max ({max_tools_warning}). "
            f"LLM performance may degrade. Consider disabling tool groups."
        )
    else:
        logger.info(f"✅ Total tools registered: {tool_count} (under {max_tools_warning} limit)")
    
    return tool_count
```

**Key Points**:
- ✅ Conditional registration (can disable)
- ✅ Tool count monitoring
- ✅ Follows existing pattern

---

## 5. Testing Strategies

### 5.1 Unit Test Pattern (Mocked Playwright)

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from mcp_server.browser_manager import BrowserManager, BrowserSession

@pytest.mark.asyncio
async def test_lazy_initialization():
    """Browser should not initialize until first use."""
    manager = BrowserManager()
    
    # No browser on construction
    assert manager._browser is None
    
    # Mock Playwright
    manager._playwright = AsyncMock()
    manager._playwright.chromium.launch = AsyncMock(return_value=MagicMock())
    
    # Initialize on first call
    await manager.initialize()
    assert manager._browser is not None


@pytest.mark.asyncio
async def test_session_isolation():
    """Different session IDs get separate contexts."""
    manager = BrowserManager()
    
    # Mock browser
    mock_browser = AsyncMock()
    mock_context_1 = AsyncMock()
    mock_context_2 = AsyncMock()
    mock_page_1 = AsyncMock()
    mock_page_2 = AsyncMock()
    
    mock_context_1.new_page = AsyncMock(return_value=mock_page_1)
    mock_context_2.new_page = AsyncMock(return_value=mock_page_2)
    
    mock_browser.new_context = AsyncMock(side_effect=[mock_context_1, mock_context_2])
    manager._browser = mock_browser
    manager._playwright = AsyncMock()
    
    # Get two different sessions
    session_a = await manager.get_session("chat-a")
    session_b = await manager.get_session("chat-b")
    
    # Different contexts
    assert session_a.context is not session_b.context
    assert session_a.page is not session_b.page
```

**Key Points**:
- ✅ Mocks external dependencies (no real browser)
- ✅ Fast execution
- ✅ Tests logic, not Playwright

---

### 5.2 Integration Test Pattern (Real Playwright)

```python
import pytest
from mcp_server.browser_manager import BrowserManager
from pathlib import Path

@pytest.mark.asyncio
@pytest.mark.integration
async def test_real_browser_navigation():
    """Test with real Playwright (requires chromium installed)."""
    manager = BrowserManager(session_timeout=60)
    
    try:
        # Get session (launches real browser)
        session = await manager.get_session("test-integration")
        
        # Navigate to example.com
        await session.page.goto("https://example.com", timeout=10000)
        title = await session.page.title()
        
        assert "Example Domain" in title
        assert session.page.url == "https://example.com/"
    
    finally:
        # Cleanup
        await manager.shutdown()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_dark_mode_screenshot():
    """Test emulate_media and screenshot."""
    manager = BrowserManager()
    screenshot_path = Path("/tmp/test_dark.png")
    
    try:
        session = await manager.get_session("test-dark")
        page = session.page
        
        # Navigate to page
        await page.goto("https://example.com")
        
        # Emulate dark mode
        await page.emulate_media(color_scheme="dark")
        
        # Take screenshot
        await page.screenshot(path=str(screenshot_path), full_page=True)
        
        # Verify file exists
        assert screenshot_path.exists()
        assert screenshot_path.stat().st_size > 1000  # Non-trivial image
    
    finally:
        if screenshot_path.exists():
            screenshot_path.unlink()
        await manager.shutdown()
```

**Key Points**:
- ✅ Marked as integration (can skip in CI)
- ✅ Cleans up resources in finally
- ✅ Tests real browser behavior

---

## 6. Troubleshooting Guide

### 6.1 Common Issues

#### Issue: Browser launch fails

**Error**:
```
RuntimeError: Failed to initialize browser: Executable doesn't exist
```

**Cause**: Chromium not installed

**Solution**:
```bash
playwright install chromium
```

---

#### Issue: TimeoutError on navigation

**Error**:
```
Navigation timeout (30000ms)
```

**Causes**:
1. Slow network
2. Page doesn't emit 'load' event
3. wait_until setting too strict

**Solutions**:
1. Increase timeout: `timeout=60000`
2. Use lenient wait: `wait_until="domcontentloaded"`
3. Check network connectivity

---

#### Issue: Zombie browser processes

**Symptom**: Multiple chromium processes remain after tests

**Cause**: Exception during cleanup

**Solution**: Ensure `shutdown()` called in finally blocks:
```python
try:
    session = await manager.get_session("test")
    # ... test code ...
finally:
    await manager.shutdown()
```

---

#### Issue: "Session not found" (Future)

**Note**: Current implementation auto-creates sessions, so this won't occur in v1.

**If strict mode added**: Call `get_session()` before using session_id in tool

---

### 6.2 Debugging Tips

**Enable debug logging**:
```python
import logging
logging.getLogger("mcp_server.browser_manager").setLevel(logging.DEBUG)
logging.getLogger("mcp_server.server.tools.browser_tools").setLevel(logging.DEBUG)
```

**Monitor active sessions**:
```python
logger.info(f"Active sessions: {list(browser_manager._sessions.keys())}")
logger.info(f"Session count: {len(browser_manager._sessions)}")
```

**Check browser process**:
```bash
ps aux | grep chromium
```

**Playwright debugging**:
```bash
PLAYWRIGHT_DEBUG=1 python -m mcp_server
```

---

## 7. Deployment Checklist

### Pre-Deployment

- [ ] All unit tests pass (`pytest tests/unit/test_browser_manager.py`)
- [ ] All integration tests pass (`pytest tests/integration/test_browser_tools.py`)
- [ ] Code coverage >80% (`pytest --cov=mcp_server`)
- [ ] No linter errors (`ruff check mcp_server/`)
- [ ] All docstrings present (Sphinx format)
- [ ] Concurrency analysis documented (`CONCURRENCY_ANALYSIS.md`)

### Deployment Steps

1. **Install Playwright**:
   ```bash
   pip install playwright>=1.40.0
   playwright install chromium
   ```

2. **Update Config**:
   Add to `.praxis-os/config.json`:
   ```json
   {
     "mcp": {
       "enabled_tool_groups": ["rag", "workflow", "browser"]
     }
   }
   ```

3. **Update Auto-Approve**:
   Add to `.cursor/mcp.json`:
   ```json
   {
     "mcpServers": {
       "agent-os-rag": {
         "autoApprove": ["search_standards", "get_current_phase", "pos_browser"]
       }
     }
   }
   ```

4. **Restart MCP Server**:
   ```bash
   # Cursor will auto-restart on config change
   ```

5. **Verify Tool Available**:
   In Cursor chat:
   ```
   pos_browser(action="navigate", url="https://example.com")
   ```

### Post-Deployment Validation

- [ ] Tool appears in MCP tool list
- [ ] Can navigate to example.com
- [ ] Can emulate dark mode
- [ ] Can capture screenshot
- [ ] Multi-session isolation works
- [ ] Cleanup happens (check `ps aux | grep chromium` after close)

---

## 8. Performance Optimization

### 8.1 Cold Start Optimization

**Current**: Browser launches on first `pos_browser()` call (lazy)

**Alternative**: Pre-warm on server startup
```python
# In ServerFactory.create_server()
await browser_manager.initialize()  # Eager init
```

**Trade-off**: Slower server startup, faster first tool call

**Recommendation**: Keep lazy (current) - better UX for most users

---

### 8.2 Session Reuse

**Key Metric**: Same session_id = reuse same page

**Ensure**:
- Use consistent session_id across tool calls
- Don't close session until workflow complete
- Monitor `last_access` to verify reuse

---

### 8.3 Resource Limits

**Current Limits**:
- Session timeout: 3600s (1 hour)
- No max session count (relies on timeout)

**Future Enhancement**: Add max_sessions config:
```python
if len(self._sessions) >= self.max_sessions:
    # Close oldest session
    oldest = min(self._sessions.items(), key=lambda x: x[1].last_access)
    await self.close_session(oldest[0])
```

---

**Phase 4 Complete** - Ready for Phase 5 (Testing & Validation)

