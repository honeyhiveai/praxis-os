# Tool Naming Strategy - Avoiding Collisions

**Critical Issue**: Cursor has its own tools AND Playwright MCP integration. We must avoid naming conflicts.

---

## 🔍 Current Tool Landscape

### Cursor's Built-in Tools
From this conversation, Cursor provides:
- `read_file` - Read file contents
- `write` - Write file
- `search_replace` - Edit files
- `run_terminal_cmd` - Execute commands
- `grep` - Search with ripgrep
- `codebase_search` - Semantic code search
- `list_dir` - List directory contents
- `glob_file_search` - Find files by pattern
- `delete_file` - Delete files
- `web_search` - Web search
- `update_memory` - Memory management
- `read_lints` - Read linter errors
- `edit_notebook` - Edit Jupyter notebooks
- `todo_write` - Task management

### Cursor's Playwright MCP Tools
Cursor has an existing Playwright MCP server with tools like:
- `mcp_cursor-playwright_browser_navigate`
- `mcp_cursor-playwright_browser_screenshot`
- `mcp_cursor-playwright_browser_click`
- `mcp_cursor-playwright_browser_snapshot`
- `mcp_cursor-playwright_browser_evaluate`
- ... (many more)

**Key Observation**: Cursor's Playwright tools are **namespaced** with `mcp_cursor-playwright_` prefix.

### Agent OS Enhanced MCP Tools (Current)
From `.cursor/mcp.json` and our codebase:
- `search_standards` ✅ No conflict
- `start_workflow` ✅ No conflict
- `get_current_phase` ✅ No conflict
- `get_task` ✅ No conflict
- `complete_phase` ✅ No conflict
- `get_workflow_state` ✅ No conflict
- `create_workflow` ✅ No conflict
- `current_date` ✅ No conflict

**Current Status**: No namespacing, but no conflicts (yet).

---

## 🚨 Potential Collision Scenarios

### Scenario 1: Direct Name Collision
```
Cursor tool: browser()
Our tool:     browser()
→ ❌ COLLISION
```

### Scenario 2: Cursor Playwright MCP Already Has `browser`
```
Cursor:  mcp_cursor-playwright_browser()
Our MCP: browser()
→ ⚠️  Different names, but confusing
```

### Scenario 3: Future Cursor Feature
```
Today:    No collision
Future:   Cursor adds browser() built-in
Our tool: browser()
→ ❌ COLLISION (breaking change)
```

---

## 📋 Naming Options

### Option A: No Namespace (Simple)
```python
@mcp.tool()
async def browser(action: str, **kwargs) -> Dict:
    """Browser automation tool."""
```

**Pros:**
- ✅ Clean, simple name
- ✅ Easy to remember
- ✅ Matches how our other tools are named

**Cons:**
- ❌ Could conflict with future Cursor features
- ❌ Ambiguous when multiple MCP servers provide browser tools
- ❌ No clear ownership

**Risk Level**: Medium (no current conflict, but future risk)

### Option B: Server Prefix (Recommended)
```python
@mcp.tool()
async def aos_browser(action: str, **kwargs) -> Dict:
    """Agent OS browser automation tool."""
```

**Naming Convention**: `aos_` (Agent OS) prefix
- `aos_browser` - Browser automation
- `aos_persona` (future) - Persona consultations
- Current tools unchanged (grandfather them in)

**Pros:**
- ✅ Clear ownership (Agent OS)
- ✅ No conflict with Cursor tools
- ✅ Future-proof
- ✅ Consistent namespace for new tools

**Cons:**
- ⚠️ Slightly longer name
- ⚠️ Inconsistent with existing tools (search_standards, start_workflow)

**Risk Level**: Very Low

### Option C: Full Server Name Prefix
```python
@mcp.tool()
async def agent_os_browser(action: str, **kwargs) -> Dict:
    """Agent OS browser automation tool."""
```

**Pros:**
- ✅ Maximum clarity
- ✅ Matches MCP server name ("agent-os-rag")
- ✅ Zero collision risk

**Cons:**
- ❌ Very long name (16 characters before action)
- ❌ Verbose for common operations
- ❌ Inconsistent with existing tools

**Risk Level**: Very Low (but overkill)

### Option D: Domain Prefix (Alternative)
```python
@mcp.tool()
async def agentbrowser(action: str, **kwargs) -> Dict:
    """Agent-controlled browser automation."""
```

**Pros:**
- ✅ Clear it's agent-driven (not user-driven)
- ✅ Single word (easier for LLM)
- ✅ Differentiates from Cursor's browser tools

**Cons:**
- ⚠️ Less clear ownership
- ⚠️ Could still conflict if Cursor adds "agentbrowser"

**Risk Level**: Low-Medium

---

## 🎯 Recommended Strategy

### **Use `aos_` Prefix for New Tools**

**Naming Pattern**:
```
aos_browser         - Browser automation (consolidated tool)
aos_persona         - Persona consultations (future)
aos_*               - Any future specialized tools
```

**Keep Existing Tools Unchanged**:
```
search_standards    - Core RAG functionality
start_workflow      - Core workflow functionality
get_current_phase   - Core workflow functionality
... (all existing tools)
```

**Rationale**:
1. **No Breaking Changes**: Existing tools keep their names
2. **Clear Namespace**: New tools clearly belong to Agent OS
3. **Future-Proof**: Won't conflict with Cursor additions
4. **Reasonable Length**: `aos_` is short (4 chars)
5. **Discoverable**: AI can easily find "Agent OS tools" by prefix

---

## 📊 Name Collision Check

### Current Agent OS Tools vs Cursor Built-ins

| Agent OS Tool | Cursor Conflict? | Safe? |
|---------------|------------------|-------|
| `search_standards` | No Cursor tool with this name | ✅ Safe |
| `start_workflow` | No Cursor tool with this name | ✅ Safe |
| `get_current_phase` | No Cursor tool with this name | ✅ Safe |
| `get_task` | No Cursor tool with this name | ✅ Safe |
| `complete_phase` | No Cursor tool with this name | ✅ Safe |
| `get_workflow_state` | No Cursor tool with this name | ✅ Safe |
| `create_workflow` | No Cursor tool with this name | ✅ Safe |
| `current_date` | No Cursor tool with this name | ✅ Safe |

### Proposed New Tool vs Cursor

| Proposed Name | Cursor Conflict? | Analysis |
|---------------|------------------|----------|
| `browser` | No direct conflict, but Cursor has `mcp_cursor-playwright_browser_*` | ⚠️ Potentially confusing |
| `aos_browser` | No conflict | ✅ **SAFE** |
| `agent_os_browser` | No conflict | ✅ Safe but verbose |

---

## 🔧 Implementation

### Tool Registration with Namespace

```python
# mcp_server/server/tools/browser_tools.py

def register_browser_tools(mcp: Any, browser_manager: Any) -> int:
    """
    Register browser automation tools with MCP server.
    
    Tool name: aos_browser (Agent OS Browser)
    Namespace: aos_ (Agent OS)
    """
    
    @mcp.tool()
    async def aos_browser(
        action: str,
        url: Optional[str] = None,
        color_scheme: Optional[str] = None,
        viewport_width: Optional[int] = None,
        viewport_height: Optional[int] = None,
        screenshot_full_page: bool = False,
        screenshot_path: Optional[str] = None,
        screenshot_format: str = "png",
        wait_until: str = "load",
        timeout: int = 30000,
    ) -> Dict[str, Any]:
        """
        Agent OS browser automation tool.
        
        Provides browser automation with persistent session management.
        Complementary to Cursor's Playwright tools but with Agent OS integration.
        
        Actions:
            navigate: Navigate to URL
            emulate_media: Set color scheme (dark mode) and media features
            screenshot: Capture page screenshot
            set_viewport: Resize browser window
            get_console: Get console messages
            close: Close browser session
        
        ... [rest of docstring]
        """
        # Implementation
        pass
    
    logger.info("Registered 1 browser tool: aos_browser")
    return 1
```

### Usage Examples

**For AI Agent:**
```python
# Enable dark mode on docs site
aos_browser(action="navigate", url="http://localhost:3000")
aos_browser(action="emulate_media", color_scheme="dark")
aos_browser(action="screenshot", screenshot_path="/tmp/dark-mode.png")
```

**In Documentation:**
```markdown
## Browser Automation

Agent OS provides the `aos_browser` tool for programmatic browser control:

- Test documentation sites in light/dark mode
- Capture screenshots for validation
- Automate visual regression testing

Note: This complements Cursor's Playwright tools with Agent OS-specific features.
```

---

## 🎨 Naming Consistency Guidelines

### For Future Tools

**New specialized tools should use `aos_` prefix:**

| Tool | Name | Rationale |
|------|------|-----------|
| Browser automation | `aos_browser` | Clear namespace, avoids confusion |
| Persona consultations | `aos_persona` | Clear namespace |
| Custom validators | `aos_validate_*` | Clear namespace |
| Domain-specific tools | `aos_*` | Clear namespace |

**Core RAG/Workflow tools keep existing names:**

| Tool | Keep Name | Rationale |
|------|-----------|-----------|
| RAG search | `search_standards` | Core functionality, no conflict risk |
| Workflow management | `start_workflow`, `get_task`, etc. | Core functionality, established |

### Naming Rules

1. **New tool?** → Use `aos_` prefix
2. **Core RAG/workflow?** → No prefix (established pattern)
3. **Multiple words?** → Use snake_case: `aos_browser_session`, `aos_run_persona`
4. **Ambiguous?** → Add prefix for safety

---

## ✅ Final Recommendation

**Tool Name**: `aos_browser`

**Full Signature**:
```python
async def aos_browser(
    action: str,
    url: Optional[str] = None,
    color_scheme: Optional[str] = None,
    # ... other params
) -> Dict[str, Any]:
    """Agent OS browser automation tool."""
```

**Benefits**:
- ✅ No collision with Cursor's tools
- ✅ Clear ownership (Agent OS)
- ✅ Future-proof
- ✅ Short enough to be practical (11 chars)
- ✅ Establishes namespace pattern for future tools

**Tool Count**:
```
Current:     8 tools
+ Browser:   1 tool (aos_browser)
─────────────────────
Total:       9 tools ✅ (well under 20-tool limit)
```

---

## 📝 Documentation Updates Needed

1. **RESEARCH.md**: Update all `browser()` references to `aos_browser()`
2. **TOOL_CONSOLIDATION.md**: Update tool names
3. **SUMMARY.md**: Update tool name
4. **MCP Server README**: Document naming convention
5. **Usage Examples**: Update all code samples

---

**Proceed with `aos_browser` as the tool name!** 🎯

