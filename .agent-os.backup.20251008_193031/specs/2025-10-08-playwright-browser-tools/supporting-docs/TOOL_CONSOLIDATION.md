# Tool Consolidation Strategy

**Date**: October 8, 2025  
**Issue**: MCP tool limit of 20 (85% performance drop beyond this)

---

## 📊 Current Tool Count Analysis

### Existing Tools (8 total)
| Group | Tool | Purpose |
|-------|------|---------|
| RAG | `search_standards()` | Semantic search over standards |
| Workflow | `start_workflow()` | Initialize workflow |
| Workflow | `get_current_phase()` | Get phase content |
| Workflow | `get_task()` | Get specific task (horizontal scaling) |
| Workflow | `complete_phase()` | Submit evidence & advance |
| Workflow | `get_workflow_state()` | Get workflow state |
| Workflow | `create_workflow()` | Generate new workflow |
| Workflow | `current_date()` | Get timestamp (prevent AI date errors) |

**Current Total: 8 tools**

### Proposed Additions

**Browser Tools (Original Proposal)**: 6 tools
- `browser_navigate()`
- `browser_emulate_media()`
- `browser_screenshot()`
- `browser_set_viewport()`
- `browser_get_console()`
- `browser_close()`

**Persona Tools (Upcoming)**: 9 tools (if granular)
- One per persona (design, concurrency, architecture, etc.)

**Problem**:
```
8 (current) + 6 (browser) + 9 (persona) = 23 tools ❌ OVER LIMIT
```

---

## 🎯 Consolidated Design Strategy

### Option A: Minimal Consolidation (Recommended)

**Consolidate both Browser and Persona into single tools:**

| Group | Tool | Count | Design |
|-------|------|-------|--------|
| Existing | (no change) | 8 | Keep as-is |
| Browser | `browser()` | 1 | Action-based parameter |
| Persona | `ask_persona()` | 1 | Persona-based parameter |

**New Total: 10 tools** ✅ **Well under limit with room to grow**

### Option B: Selective Consolidation

**Consolidate Persona only, keep Browser granular:**

| Group | Tool | Count |
|-------|------|-------|
| Existing | (no change) | 8 |
| Browser | `browser_*()` | 6 |
| Persona | `ask_persona()` | 1 |

**New Total: 15 tools** ✅ **Under limit, but tight**

---

## 🏗️ Recommended Design: Consolidated Browser Tool

### Single Tool with Action Parameter

```python
@mcp.tool()
async def browser(
    action: str,
    url: Optional[str] = None,
    # Context/viewport options
    color_scheme: Optional[str] = None,
    viewport_width: Optional[int] = None,
    viewport_height: Optional[int] = None,
    # Screenshot options
    screenshot_full_page: bool = False,
    screenshot_path: Optional[str] = None,
    screenshot_format: str = "png",
    # Navigation options
    wait_until: str = "load",
    timeout: int = 30000,
) -> Dict[str, Any]:
    """
    Browser automation tool with multiple actions.
    
    Actions:
        navigate: Navigate to URL
        emulate_media: Set color scheme (dark mode) and media features
        screenshot: Capture page screenshot
        set_viewport: Resize browser window
        get_console: Get console messages
        close: Close browser session
    
    Examples:
        # Navigate to URL
        browser(action="navigate", url="https://example.com")
        
        # Enable dark mode
        browser(action="emulate_media", color_scheme="dark")
        
        # Take full-page screenshot
        browser(action="screenshot", screenshot_full_page=True, screenshot_path="/tmp/screenshot.png")
        
        # Set viewport
        browser(action="set_viewport", viewport_width=1920, viewport_height=1080)
        
        # Get console logs
        browser(action="get_console")
        
        # Close browser
        browser(action="close")
    
    Args:
        action: Action to perform (navigate, emulate_media, screenshot, set_viewport, get_console, close)
        url: Target URL (for navigate action)
        color_scheme: 'light', 'dark', or 'no-preference' (for emulate_media)
        viewport_width: Viewport width in pixels (for set_viewport)
        viewport_height: Viewport height in pixels (for set_viewport)
        screenshot_full_page: Capture full scrollable page (for screenshot)
        screenshot_path: File path to save screenshot (for screenshot)
        screenshot_format: 'png' or 'jpeg' (for screenshot)
        wait_until: Wait condition for navigation ('load', 'domcontentloaded', 'networkidle')
        timeout: Timeout in milliseconds
    
    Returns:
        Action-specific result dictionary
    """
    try:
        page = await browser_manager.get_or_create_page()
        
        if action == "navigate":
            if not url:
                return {"status": "error", "error": "url required for navigate action"}
            await page.goto(url, wait_until=wait_until, timeout=timeout)
            return {
                "status": "success",
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
                "applied": media_features
            }
        
        elif action == "screenshot":
            screenshot_options = {
                "full_page": screenshot_full_page,
                "type": screenshot_format
            }
            if screenshot_path:
                screenshot_options["path"] = screenshot_path
            
            screenshot_bytes = await page.screenshot(**screenshot_options)
            
            result = {"status": "success"}
            if screenshot_path:
                result["path"] = screenshot_path
            else:
                import base64
                result["data"] = base64.b64encode(screenshot_bytes).decode()
            
            return result
        
        elif action == "set_viewport":
            if not viewport_width or not viewport_height:
                return {"status": "error", "error": "viewport_width and viewport_height required"}
            await page.set_viewport_size({
                "width": viewport_width,
                "height": viewport_height
            })
            return {
                "status": "success",
                "viewport": {"width": viewport_width, "height": viewport_height}
            }
        
        elif action == "get_console":
            # TODO: Implement console message collection
            return {"status": "success", "messages": []}
        
        elif action == "close":
            await browser_manager.shutdown()
            return {"status": "success"}
        
        else:
            return {
                "status": "error",
                "error": f"Unknown action: {action}. Valid actions: navigate, emulate_media, screenshot, set_viewport, get_console, close"
            }
    
    except Exception as e:
        logger.error(f"browser action '{action}' failed: {e}")
        return {"status": "error", "error": str(e)}
```

### Persona Tool (Parallel Design)

```python
@mcp.tool()
async def ask_persona(
    persona: str,
    context: str,
    question: Optional[str] = None,
    target_domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Ask specialized persona for review or analysis.
    
    Personas:
        design_validator: Adversarial design review
        concurrency_analyzer: Thread safety analysis
        architecture_critic: System design review
        test_generator: Test strategy and generation
        security_reviewer: Security analysis
        performance_auditor: Performance review
        api_designer: API design review
        documentation_critic: Documentation review
        deployment_reviewer: Deployment strategy review
    
    Examples:
        # Design review
        ask_persona(
            persona="design_validator",
            context="User authentication spec...",
            target_domain="security"
        )
        
        # Concurrency analysis
        ask_persona(
            persona="concurrency_analyzer",
            context="Code snippet with threading...",
            question="Are there race conditions?"
        )
    
    Args:
        persona: Persona to consult (see list above)
        context: Code, spec, or design document to review
        question: Optional specific question to ask
        target_domain: Optional domain context for review
    
    Returns:
        Persona-specific analysis and recommendations
    """
    # Implementation delegates to appropriate sub-agent
    pass
```

---

## 📈 Comparison: Granular vs Consolidated

### Granular (Original Proposal)

**Pros:**
- ✅ Very clear, focused tools
- ✅ Easy to discover in tool list
- ✅ Simple parameters per tool

**Cons:**
- ❌ Uses 6 tool slots
- ❌ Hits 20-tool limit quickly
- ❌ No room for future growth

### Consolidated (Recommended)

**Pros:**
- ✅ Uses only 1 tool slot
- ✅ Leaves room for future tools
- ✅ Still clear with action parameter
- ✅ All related functionality in one place
- ✅ Can add new actions without new tools

**Cons:**
- ⚠️ More complex parameter surface
- ⚠️ Slightly less discoverable
- ⚠️ Longer tool docstring

---

## 🎯 Final Recommendation

**Use consolidated design for both Browser and Persona:**

```
Current:  8 tools
+ Browser: 1 tool (browser with actions)
+ Persona: 1 tool (ask_persona with personas)
─────────
Total:    10 tools ✅
```

**Benefits:**
1. **50% under limit** - Lots of room for future growth
2. **Consistent pattern** - Action-based design applies to both
3. **Extensible** - Add new actions without new tools
4. **Performant** - Well under the 20-tool degradation threshold

**Trade-offs:**
- Slightly more complex parameters
- Requires good docstrings for discoverability
- AI agents need to read tool description to know available actions

**Mitigation:**
- Excellent documentation with examples
- Clear action enumeration in docstring
- Consider MCP resources for action documentation

---

## 🚀 Updated Implementation

**Priority**: Consolidate Browser tool first (solves immediate docs testing need)

**Files to Update**:
- ✨ `mcp_server/browser_manager.py` (new, no change)
- ✨ `mcp_server/server/tools/browser_tools.py` (updated design)
- 🔧 `mcp_server/server/factory.py` (no change)
- 📝 `RESEARCH.md` (reference this consolidation strategy)

**New Tool Count After Browser**: 9 tools (one under halfway mark)

---

## 📋 Next Steps

1. **Approve consolidated design** for browser tool
2. **Update RESEARCH.md** to reflect single-tool approach
3. **Consider same pattern for Persona** when implementing that feature
4. **Monitor tool count** as we add more capabilities
5. **Document action patterns** for consistency

---

**This consolidation keeps us performant and leaves room to grow!** 🎯

