# When Complex Tools Are Better Than Simple Tools
**Date**: 2025-10-15  
**Issue**: Reconsidering "simple tools" dogma  
**Insight**: Domain coherence trumps parameter count

---

## The "Simple Tools" Dogma vs. Reality

**Standard guideline**: "Simple tools with minimal parameters"

**Reality**: `aos_browser` is a **powerful, well-designed tool** with 20+ parameters

**Question**: Why does this work so well when it violates the "simple tools" principle?

**Answer**: Domain coherence matters more than parameter count.

---

## Why aos_browser Is Actually Well-Designed

### 1. Domain Coherence

**Browser automation is a single, coherent domain:**
- All actions operate on the **same entity** (browser page/session)
- All actions share **common context** (session_id, page state)
- Actions are **naturally sequential** (navigate → wait → click → type → screenshot)

**Single tool models this domain accurately:**
```python
aos_browser(action="navigate", session_id="test1", url="https://example.com")
aos_browser(action="wait", session_id="test1", selector="#button", wait_for_state="visible")
aos_browser(action="click", session_id="test1", selector="#button")
aos_browser(action="screenshot", session_id="test1", screenshot_path="result.png")
```

**The action parameter provides clarity** about what operation is being performed, and only the relevant parameters for that action matter.

### 2. Tool Count Economics

**Alternative (granular browser tools)**:
```python
# Would require ~20 separate tools
browser_navigate(session_id, url)
browser_wait(session_id, selector, state)
browser_click(session_id, selector)
browser_type(session_id, selector, text)
browser_fill(session_id, selector, value)
browser_select(session_id, selector, value)
browser_screenshot(session_id, path)
browser_evaluate(session_id, script)
browser_get_cookies(session_id)
browser_set_cookies(session_id, cookies)
browser_get_local_storage(session_id, key)
browser_emulate_media(session_id, color_scheme)
browser_viewport(session_id, width, height)
browser_query(session_id, selector)
browser_intercept_network(session_id, pattern, handler)
browser_new_tab(session_id, url)
browser_switch_tab(session_id, tab_id)
browser_close_tab(session_id, tab_id)
browser_list_tabs(session_id)
browser_upload_file(session_id, selector, file_path)
browser_download_file(session_id, trigger_selector, file_path)
# ... etc
```

**Impact**:
- Current: 11 tools total
- With granular browser: **~30 tools** (degraded performance zone)

**Cost**: 85% performance degradation, 40% error rate

**Benefit**: Marginal clarity improvement, not worth the cost

### 3. Shared Context Pattern

**Every browser action requires session_id** as the first parameter.

**This is a code smell for "should be one tool":**
```python
# All these have identical first parameter
browser_navigate(session_id, ...)
browser_click(session_id, ...)
browser_screenshot(session_id, ...)
```

**When context is shared, consolidation makes sense:**
```python
# Single tool, action dispatch based on shared context
aos_browser(action="...", session_id="...", ...)
```

### 4. Parameter Clarity Through Action Dispatch

**Despite 20+ parameters, the design is clear:**

```python
aos_browser(
    action: str,              # ← Determines which parameters matter
    session_id: Optional[str],
    
    # Navigation params (only for action="navigate")
    url: Optional[str],
    wait_until: str = "load",
    
    # Screenshot params (only for action="screenshot")
    screenshot_path: Optional[str],
    screenshot_format: str = "png",
    
    # Click params (only for action="click")
    selector: Optional[str],
    button: str = "left",
    
    # etc.
)
```

**The action parameter acts as a discriminator**: It tells the LLM which parameters are relevant for this call.

**Example call clarity**:
```python
# Navigate: Only url and wait_until matter
aos_browser(action="navigate", session_id="test", url="https://...", wait_until="load")

# Click: Only selector and button matter
aos_browser(action="click", session_id="test", selector="#submit", button="left")

# Screenshot: Only screenshot_path and screenshot_format matter
aos_browser(action="screenshot", session_id="test", screenshot_path="./result.png")
```

**LLM doesn't need to understand all 20+ parameters for every call** - only the subset relevant to the action.

### 5. Operational Coherence

**Browser operations are stateful and sequential:**
1. Navigate to page
2. Wait for elements
3. Interact with elements (click, type, fill)
4. Capture results (screenshot, evaluate)
5. Clean up session

**Single tool with session_id maintains state across operations:**
```python
# Coherent workflow with persistent session
session_id = "test_checkout"

aos_browser(action="navigate", session_id=session_id, url="https://shop.com")
aos_browser(action="wait", session_id=session_id, selector="#product")
aos_browser(action="click", session_id=session_id, selector="#add-to-cart")
aos_browser(action="type", session_id=session_id, selector="#quantity", text="5")
aos_browser(action="screenshot", session_id=session_id, screenshot_path="cart.png")
aos_browser(action="close", session_id=session_id)
```

**This models real browser automation workflows accurately.**

---

## The Real Principle: Domain-Appropriate Complexity

### Not "Simple Tools Always"

**The real principle**: **Match tool complexity to domain complexity**

**Simple domain → Simple tool:**
```python
# Workflow state is conceptually simple
get_current_phase(session_id)  # 1 param: get current phase
```

**Complex domain → Complex tool:**
```python
# Browser automation is conceptually complex
aos_browser(
    action="...",          # What to do
    session_id="...",      # Which browser session
    # + domain-specific parameters
)
```

### Decision Framework

**Use GRANULAR tools when:**
- ✅ Actions are conceptually distinct
- ✅ Different domains/contexts (workflows vs. search vs. validation)
- ✅ Independent execution (don't share session/state)
- ✅ Different authorization requirements
- ✅ Tool count permits (each adds 1 to count)

**Example**: Workflow tools (start_workflow, get_task, complete_phase)
- Different conceptual operations
- Different stages of workflow lifecycle
- Can be called independently
- Minimal shared context beyond session_id

**Use PARAMETERIZED tool when:**
- ✅ Single coherent domain (browser, file operations, database)
- ✅ Shared context required (session_id, connection, handle)
- ✅ Sequential operations on same entity (page, file, database)
- ✅ Tool count economics favor consolidation (20 tools → 1 tool)
- ✅ Action parameter provides clarity

**Example**: Browser automation (aos_browser)
- Single domain: browser interactions
- Shared context: browser session/page
- Sequential: navigate → interact → capture
- Economics: 20 granular tools vs. 1 parameterized tool

---

## Examples of Domain-Appropriate Complexity

### ✅ GOOD: Simple Workflow Tools (Distinct Operations)

```python
# Conceptually distinct operations, minimal shared context
start_workflow(workflow_type, target_file)     # Initialize
get_current_phase(session_id)                  # Retrieve state
get_task(session_id, phase, task_number)       # Retrieve content
complete_phase(session_id, phase, evidence)    # Validate & advance
```

**Why simple works**:
- Each operation is conceptually separate
- Not sequential operations on same entity
- Different purposes (initialize vs. retrieve vs. validate)
- Minimal context sharing

### ✅ GOOD: Complex Browser Tool (Single Domain)

```python
# Single domain with many operations, heavy context sharing
aos_browser(action="navigate", session_id, url, ...)
aos_browser(action="click", session_id, selector, ...)
aos_browser(action="screenshot", session_id, path, ...)
```

**Why complex works**:
- All operations on same entity (browser page)
- Sequential workflow (navigate → interact → capture)
- Heavy context sharing (session maintains state)
- Tool count economics (1 tool vs. 20 tools)

### ❌ BAD: Overly Simple (Artificial Splitting)

```python
# Artificially splitting a coherent domain
browser_navigate(session_id, url)
browser_navigate_wait_until_load(session_id, url)
browser_navigate_wait_until_networkidle(session_id, url)
```

**Why this is bad**:
- Splits one operation (navigate) into 3 tools
- Artificial distinction (wait_until is just a parameter)
- Increases tool count unnecessarily
- No clarity benefit

### ❌ BAD: Overly Complex (Domain Mixing)

```python
# Mixing unrelated domains into one tool
universal_automation(
    action: str,  # "workflow_start" | "browser_click" | "search_rag" | "validate_yaml"
    # ... 50+ parameters for all domains
)
```

**Why this is bad**:
- Mixes unrelated domains (workflows, browser, search, validation)
- No conceptual coherence
- Parameter explosion without clarity
- Hard to document and understand

---

## Case Study: Why aos_browser Beats 20 Granular Tools

### Scenario: Test dark mode on a website

**With aos_browser (1 tool, multiple calls)**:
```python
# Clear, coherent workflow
aos_browser(action="navigate", session_id="dark-test", url="http://localhost:3000")
aos_browser(action="emulate_media", session_id="dark-test", color_scheme="dark")
aos_browser(action="screenshot", session_id="dark-test", screenshot_path="dark.png")
aos_browser(action="emulate_media", session_id="dark-test", color_scheme="light")
aos_browser(action="screenshot", session_id="dark-test", screenshot_path="light.png")
aos_browser(action="close", session_id="dark-test")
```

**Tool count**: 11 total (1 browser tool + 10 others)

**With granular browser tools (20 tools, multiple calls)**:
```python
# Unclear which "namespace" each tool belongs to
browser_navigate(session_id="dark-test", url="http://localhost:3000")
browser_emulate_media(session_id="dark-test", color_scheme="dark")
browser_screenshot(session_id="dark-test", path="dark.png")
browser_emulate_media(session_id="dark-test", color_scheme="light")
browser_screenshot(session_id="dark-test", path="light.png")
browser_close(session_id="dark-test")
```

**Tool count**: ~30 total (20 browser tools + 10 others)

**Performance**: 85% degradation, 40% error rate

### Which is Better?

**aos_browser approach wins because**:
1. ✅ Same code clarity (both are readable)
2. ✅ 11 tools vs. 30 tools (optimal vs. degraded performance)
3. ✅ Clear namespace (aos_browser.action tells you it's browser-related)
4. ✅ Session management is explicit (session_id in every call)
5. ✅ Easy to add new browser actions (just add action type, not new tool)

**Granular approach loses because**:
1. ❌ No clarity advantage (same workflow steps)
2. ❌ 30 tools (85% performance degradation)
3. ❌ Unclear namespace (is browser_click browser or generic?)
4. ❌ Hard to extend (each new action = new tool = tool count penalty)

---

## Comparison: Workflow Tools vs. Browser Tools

### Why Workflow Tools Are Granular (Correct Design)

**Workflow operations are conceptually distinct:**

1. **start_workflow**: Initialize a new workflow session
   - Creates session
   - Loads metadata
   - Returns Phase 0 content
   - **Not related to** other workflow operations

2. **get_task**: Retrieve specific task content
   - Loads task.md file
   - Parses commands
   - Returns structured content
   - **Independent operation** (doesn't modify state)

3. **complete_phase**: Validate evidence and advance
   - Validates checkpoint
   - Stores artifacts
   - Advances to next phase
   - **State mutation** (changes workflow state)

**These are DIFFERENT operations with DIFFERENT purposes:**
- Initialize vs. retrieve vs. mutate
- Different parameters (workflow_type vs. task_number vs. evidence)
- Different error conditions
- Different authorization requirements

**Consolidating these would be WRONG:**
```python
# BAD: Mixing distinct operations
workflow(
    action: str,  # "start" | "get_task" | "complete_phase"
    session_id: Optional[str],
    workflow_type: Optional[str],
    phase: Optional[int],
    task_number: Optional[int],
    evidence: Optional[Dict]
)
```

**Why this is bad**:
- Forces all optional parameters (which params for which action?)
- No conceptual coherence (initialize, retrieve, mutate are different)
- Poor error messages (validation depends on action)
- Hard to document

### Why Browser Tool Is Parameterized (Correct Design)

**Browser operations are variations of the same operation:**

All browser actions are **operations on a browser page**:
- Navigate page
- Click element on page
- Type text on page
- Screenshot page
- Evaluate script on page

**Shared context**: browser session/page  
**Sequential workflow**: operations build on each other  
**Conceptual coherence**: all manipulate the same entity

**Consolidating makes sense:**
```python
# GOOD: Single domain with action dispatch
aos_browser(
    action: str,  # "navigate" | "click" | "screenshot" | ...
    session_id: str,  # ← ALWAYS required (shared context)
    # + action-specific params
)
```

**Why this works**:
- Session_id is always required (shared context)
- Action parameter provides clarity
- All operations on same entity (browser page)
- Tool count economics (1 tool vs. 20 tools)

---

## Updated Guidelines

### ❌ OLD: "Always use simple tools with minimal parameters"

This is too dogmatic and misses important nuances.

### ✅ NEW: "Match tool complexity to domain complexity"

**Ask these questions**:

1. **Is this a single coherent domain?**
   - Yes → Parameterized tool may be better (aos_browser)
   - No → Granular tools (workflow operations)

2. **Do all operations share context?**
   - Yes → Parameterized tool (session_id, connection, handle)
   - No → Granular tools (independent operations)

3. **Are operations sequential on same entity?**
   - Yes → Parameterized tool (browser page, file handle)
   - No → Granular tools (workflow lifecycle stages)

4. **What's the tool count impact?**
   - Split adds 10+ tools → Consider parameterized
   - Split adds 2-3 tools → Granular is fine

5. **Does action parameter add clarity?**
   - Yes → Parameterized tool (aos_browser action types are clear)
   - No → Granular tools (action would be confusing)

---

## Real-World Examples

### Domains That Should Be Parameterized Tools

**1. File Operations**
```python
# GOOD: Single domain (file I/O)
file_operation(
    action: str,  # "read" | "write" | "append" | "delete"
    file_path: str,
    content: Optional[str],
    mode: Optional[str]
)
```

**Why**: All operations on files, shared context (file path), tool count economics

**2. Database Queries**
```python
# GOOD: Single domain (database)
database(
    action: str,  # "query" | "insert" | "update" | "delete"
    connection_id: str,
    query: Optional[str],
    params: Optional[Dict]
)
```

**Why**: All operations on database, shared context (connection), sequential operations

**3. Browser Automation** (aos_browser)
```python
# GOOD: Single domain (browser)
aos_browser(
    action: str,  # "navigate" | "click" | "screenshot" | ...
    session_id: str,
    # + action-specific params
)
```

**Why**: All operations on browser page, shared context (session), sequential workflow

### Domains That Should Be Granular Tools

**1. Workflow Lifecycle**
```python
# GOOD: Distinct operations
start_workflow(workflow_type, target_file)
get_task(session_id, phase, task_number)
complete_phase(session_id, phase, evidence)
```

**Why**: Conceptually distinct (initialize vs. retrieve vs. validate), minimal shared context

**2. Search & Validation**
```python
# GOOD: Different purposes
search_standards(query, n_results, filters)
validate_workflow(workflow_path)
create_workflow(name, phases)
```

**Why**: Unrelated operations, different domains, different purposes

**3. System Information**
```python
# GOOD: Independent queries
get_server_info()
current_date()
list_workflows(filter_by)
```

**Why**: Independent operations, no shared context, different information domains

---

## Conclusion

### Key Insights

1. **Domain coherence matters more than parameter count**
   - aos_browser is well-designed BECAUSE it models a single domain
   - 20+ parameters are fine when they're organized by action type

2. **Tool count economics are real**
   - Splitting aos_browser → 20 tools → 30 total → 85% degradation
   - Keeping aos_browser → 1 tool → 11 total → optimal performance

3. **Shared context is a strong signal for consolidation**
   - All browser operations need session_id → parameterized tool
   - Workflow operations have minimal shared context → granular tools

4. **Action parameter provides clarity**
   - aos_browser(action="click") is clear
   - Not confusing which parameters matter for each action
   - Better than 20 separate tools polluting tool catalog

### Updated Principle

**NOT**: "Simple tools with minimal parameters"

**BUT**: "Domain-appropriate tool complexity"

- ✅ Simple domains → simple tools
- ✅ Complex domains → complex tools (when coherent)
- ❌ Artificial splitting → hurts performance
- ❌ Domain mixing → hurts clarity

### aos_browser Is Exemplary Design

**It's not an exception to the rule - it's an example of the CORRECT rule applied properly:**
- Single coherent domain (browser automation)
- Shared context (session_id)
- Sequential operations (navigate → interact → capture)
- Tool count economics (1 tool vs. 20 tools)
- Action parameter provides clarity

**The lesson**: Don't be dogmatic about "simple tools". Think about the domain you're modeling.

