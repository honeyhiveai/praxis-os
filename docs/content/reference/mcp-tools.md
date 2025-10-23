---
sidebar_position: 1
doc_type: reference
---

# MCP Tools Reference

Comprehensive API reference for Agent OS Enhanced MCP (Model Context Protocol) tools.

## Overview

Agent OS Enhanced provides tools for semantic search, workflow execution, and browser automation. Tools are organized into groups for selective loading to maintain optimal LLM performance (under 20 tools).

**Tool Groups:**
- `rag` - Semantic search over standards and documentation
- `workflow` - Phase-gated workflow execution and creation
- `browser` - Browser automation with Playwright

**Configuration:** Enable/disable groups in `.agent-os/config.json`:
```json
{
  "enabled_tool_groups": ["rag", "workflow", "browser"]
}
```

---

## RAG Tools

### `search_standards`

Semantic search over universal standards, usage guides, and workflows.

**Purpose:** 90% context reduction - find relevant chunks without reading entire files.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | Natural language question about standards/workflows |
| `n_results` | integer | No | Number of results to return (default: 5) |
| `filter_phase` | integer | No | Filter by workflow phase number (1-8) |
| `filter_tags` | array[string] | No | Filter by tags (e.g., `["testing", "concurrency"]`) |

**Returns:** `Dict[str, Any]` - Search results with content chunks, file paths, and relevance scores.

```python
{
  "results": [
    {
      "content": "Chunk content...",
      "file": "standards/concurrency/race-conditions.md",
      "section": "Detection Strategies",
      "relevance_score": 0.89,
      "tokens": 156
    }
  ],
  "total_tokens": 753,
  "retrieval_method": "vector",
  "query_time_ms": 132.8
}
```

**Examples:**

```python
# Basic query
search_standards(
    query="How do I handle race conditions in shared state?",
    n_results=3
)

# Filtered by phase
search_standards(
    query="testing concurrency",
    filter_phase=3,
    n_results=5
)

# Filtered by tags
search_standards(
    query="mocking best practices",
    filter_tags=["testing", "mocking"]
)
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `No results found` | Query too specific or no indexed content | Broaden query terms, check `.agent-os/.cache/vector_index/` exists |
| `Index not found` | RAG not initialized | Wait 10-30s for file watcher to build index |

**Related:** [current_date](#current_date)

---

### `current_date`

Get current date/time for preventing date errors in AI-generated content.

**Purpose:** AI assistants frequently use cached/incorrect dates. This tool provides reliable current date/time.

**Parameters:** None

**Returns:** `Dict[str, Any]` - Current date in multiple formats.

```python
{
  "iso_date": "2025-10-12",
  "iso_datetime": "2025-10-12T14:30:00.123456",
  "day_of_week": "Sunday",
  "month": "October",
  "year": 2025,
  "unix_timestamp": 1728744600,
  "formatted": {
    "spec_directory": "2025-10-12-",
    "header": "**Date**: 2025-10-12",
    "full_readable": "Sunday, October 12, 2025"
  }
}
```

**Examples:**

```python
# Get current date for spec directory
date_info = current_date()
spec_dir = f".agent-os/specs/{date_info['iso_date']}-my-feature"

# Use in documentation header
header = f"# Feature Spec\n{date_info['formatted']['header']}\n"
```

**Errors:** None (always succeeds)

**Related:** [search_standards](#search_standards)

---

## Workflow Tools

### `aos_workflow`

Consolidated workflow management tool following action-based dispatch pattern.

**Purpose:** Single unified interface for all workflow operations - discovery, execution, management, and recovery.

#### Common Parameters

All actions accept these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Operation to perform (see actions below) |
| `session_id` | string | Conditional | Session identifier (required for most operations) |

#### Discovery Actions

**`list_workflows`** - List available workflows

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `category` | string | No | Filter by category (`"testing"`, `"documentation"`, etc.) |

```python
# List all workflows
aos_workflow(action="list_workflows")

# Filter by category
aos_workflow(action="list_workflows", category="testing")
```

**Returns:**
```python
{
  "status": "success",
  "action": "list_workflows",
  "workflows": [
    {
      "workflow_type": "spec_creation_v1",
      "name": "Spec Creation",
      "category": "documentation",
      "version": "1.0.0"
    }
  ],
  "count": 5
}
```

#### Execution Actions

**`start`** - Start new workflow session

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_type` | string | Yes | Workflow identifier (`spec_creation_v1`, etc.) |
| `target_file` | string | Yes | File or feature being worked on |

```python
aos_workflow(
    action="start",
    workflow_type="spec_creation_v1",
    target_file="user_authentication"
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "start",
  "session_id": "ed5481fe-7334-427c-bea4-c8e6103a592b",
  "workflow_type": "spec_creation_v1",
  "current_phase": 0
}
```

---

**`get_phase`** - Get current phase content

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |

```python
aos_workflow(
    action="get_phase",
    session_id="ed5481fe..."
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "get_phase",
  "current_phase": 2,
  "phase_content": {
    "title": "Phase 2: Technical Design",
    "objectives": [...],
    ...
  }
}
```

---

**`get_task`** - Get specific task details

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |
| `phase` | integer | Yes | Phase number |
| `task_number` | integer | Yes | Task number within phase |

```python
aos_workflow(
    action="get_task",
    session_id="ed5481fe...",
    phase=2,
    task_number=1
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "get_task",
  "task_content": {
    "title": "Design Data Model",
    "steps": [...],
    ...
  }
}
```

---

**`complete_phase`** - Submit evidence and complete phase

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |
| `phase` | integer | Yes | Phase number being completed |
| `evidence` | object | Yes | Evidence matching checkpoint criteria (max 10MB) |

```python
aos_workflow(
    action="complete_phase",
    session_id="ed5481fe...",
    phase=1,
    evidence={
        "srd_created": true,
        "requirements_documented": true
    }
)
```

**Returns (Success):**
```python
{
  "status": "success",
  "action": "complete_phase",
  "checkpoint_passed": true,
  "next_phase": 2
}
```

**Returns (Failure):**
```python
{
  "status": "error",
  "action": "complete_phase",
  "checkpoint_passed": false,
  "missing_evidence": ["srd_created"]
}
```

---

**`get_state`** - Get complete workflow state

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |

```python
aos_workflow(
    action="get_state",
    session_id="ed5481fe..."
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "get_state",
  "workflow_state": {
    "workflow_type": "spec_creation_v1",
    "current_phase": 3,
    "completed_phases": [0, 1, 2],
    ...
  }
}
```

#### Management Actions

**`list_sessions`** - List all workflow sessions

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Filter by status (`"active"`, `"paused"`, `"completed"`, `"error"`) |

```python
# List all sessions
aos_workflow(action="list_sessions")

# Filter by status
aos_workflow(action="list_sessions", status="active")
```

**Returns:**
```python
{
  "status": "success",
  "action": "list_sessions",
  "sessions": [
    {
      "session_id": "ed5481fe...",
      "workflow_type": "spec_creation_v1",
      "status": "active",
      "current_phase": 2
    }
  ],
  "count": 3
}
```

---

**`get_session`** - Get session details

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |

```python
aos_workflow(
    action="get_session",
    session_id="ed5481fe..."
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "get_session",
  "session_id": "ed5481fe...",
  "workflow_type": "spec_creation_v1",
  "target_file": "user_auth",
  "current_phase": 2
}
```

---

**`delete_session`** - Delete workflow session

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `session_id` | string | Yes | Workflow session identifier |

```python
aos_workflow(
    action="delete_session",
    session_id="ed5481fe..."
)
```

**Returns:**
```python
{
  "status": "success",
  "action": "delete_session",
  "session_id": "ed5481fe...",
  "deleted": true
}
```

#### Complete Example

```python
# Workflow execution lifecycle
result = aos_workflow(
    action="start",
    workflow_type="spec_creation_v1",
    target_file="auth_system"
)
session_id = result["session_id"]

# Get current phase
phase = aos_workflow(
    action="get_phase",
    session_id=session_id
)

# Get specific task
task = aos_workflow(
    action="get_task",
    session_id=session_id,
    phase=1,
    task_number=1
)

# Complete phase
aos_workflow(
    action="complete_phase",
    session_id=session_id,
    phase=1,
    evidence={"requirements_complete": true}
)

# Check state
state = aos_workflow(
    action="get_state",
    session_id=session_id
)

# Cleanup
aos_workflow(
    action="delete_session",
    session_id=session_id
)
```

#### Error Responses

All actions return structured error responses:

```python
{
  "status": "error",
  "action": "start",
  "error": "Invalid target_file: directory traversal detected",
  "error_type": "ValueError",
  "remediation": "Provide relative path within workspace"
}
```

**Common Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown action` | Invalid `action` parameter | Use valid action (see `valid_actions` in error) |
| `SessionNotFound` | Invalid `session_id` | Check session ID or start new workflow |
| `Invalid session_id format` | Malformed UUID | Provide valid UUID format |
| `directory traversal detected` | Security violation in `target_file` | Use relative paths only |
| `Evidence too large` | Evidence exceeds 10MB limit | Reduce evidence payload size |

**Related:** [create_workflow](#create_workflow), [validate_workflow](#validate_workflow)

---

## Workflow Creation Tools

### `create_workflow`

Generate new workflow framework using meta-workflow principles.

**Purpose:** Create compliant workflow structure with three-tier architecture and validation gates.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Framework name (e.g., `"api-documentation"`) |
| `workflow_type` | string | Yes | Type (e.g., `"documentation"`, `"testing"`) |
| `phases` | array[string] | Yes | Phase names (e.g., `["Analysis", "Generation"]`) |
| `target_language` | string | No | Programming language (default: `"python"`) |
| `quick_start` | boolean | No | Use minimal template (default: `true`) |
| `output_path` | string | No | Custom output path |

**Returns:** `Dict[str, Any]` - Framework details, file paths, and compliance report.

```python
{
  "workflow_name": "api-documentation",
  "phases": 3,
  "files_created": [
    ".agent-os/workflows/api-documentation/metadata.json",
    ".agent-os/workflows/api-documentation/phases/0/phase.md",
    ...
  ],
  "compliance": {
    "three_tier_architecture": true,
    "command_language": true,
    "validation_gates": true,
    "task_files_under_100_lines": true
  }
}
```

**Examples:**

```python
# Create minimal workflow
create_workflow(
    name="api-docs",
    workflow_type="documentation",
    phases=["Analysis", "Generation", "Validation"]
)

# Create workflow with custom settings
create_workflow(
    name="integration-tests",
    workflow_type="testing",
    phases=["Setup", "Execution", "Reporting"],
    target_language="typescript",
    quick_start=false,
    output_path=".agent-os/workflows/custom/"
)
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `WorkflowExists` | Workflow with name already exists | Choose different name or delete existing |
| `InvalidPhaseCount` | Too few phases (under 2) or too many (over 8) | Use 2-8 phases |
| `InvalidName` | Name contains invalid characters | Use alphanumeric and hyphens only |

**Related:** [validate_workflow](#validate_workflow)

---

### `validate_workflow`

Validate workflow structure against construction standards.

**Purpose:** Check compliance with directory structure, file naming, and size standards.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_path` | string | Yes | Path to workflow directory (e.g., `"universal/workflows/my_workflow_v1"`) |

**Returns:** `Dict[str, Any]` - Compliance status, score, issues, and warnings.

```python
{
  "workflow_path": "universal/workflows/my_workflow_v1",
  "compliant": true,
  "compliance_score": 0.95,
  "issues": [],
  "warnings": [
    {
      "type": "file_size",
      "severity": "minor",
      "file": "phases/2/task-1-implement.md",
      "message": "Task file is 185 lines (recommended: 100-170)"
    }
  ],
  "summary": "✅ Workflow compliant with standards"
}
```

**Examples:**

```python
# Validate before committing
result = validate_workflow(
    workflow_path=".agent-os/workflows/my_custom_workflow_v1"
)

if result["compliant"]:
    print("Ready to commit!")
else:
    for issue in result["issues"]:
        print(f"Fix: {issue['message']}")
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `WorkflowNotFound` | Path doesn't exist | Check path is correct |
| `InvalidStructure` | Missing required files/directories | Ensure `metadata.json` and `phases/` exist |

**Related:** [create_workflow](#create_workflow)

---

## Browser Tools

### `aos_browser`

Comprehensive browser automation with Playwright.

**Purpose:** Browser testing, automation, and inspection with persistent sessions.

#### Common Parameters

All actions accept these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform (see sections below) |
| `session_id` | string | No | Session identifier for isolation |
| `browser_type` | string | No | Browser (`"chromium"`, `"firefox"`, `"webkit"`) (default: `"chromium"`) |
| `headless` | boolean | No | Run headless (default: `true`) |
| `timeout` | integer | No | Operation timeout in ms (default: 30000) |

#### Navigation Actions

**`navigate`** - Navigate to URL

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Target URL |
| `wait_until` | string | No | Wait condition (`"load"`, `"domcontentloaded"`, `"networkidle"`) |

```python
aos_browser(
    action="navigate",
    url="http://localhost:3000",
    wait_until="networkidle",
    session_id="test-1"
)
```

#### Inspection Actions

**`screenshot`** - Capture page screenshot

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `screenshot_path` | string | Yes | File path to save screenshot |
| `screenshot_full_page` | boolean | No | Capture full scrollable page |
| `screenshot_format` | string | No | Format (`"png"`, `"jpeg"`) |

```python
aos_browser(
    action="screenshot",
    screenshot_path="/tmp/page.png",
    screenshot_full_page=true,
    session_id="test-1"
)
```

**`query`** - Query elements by selector

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `query_all` | boolean | No | Return all matches vs first |

```python
result = aos_browser(
    action="query",
    selector=".error-message",
    query_all=true,
    session_id="test-1"
)
```

**`evaluate`** - Execute JavaScript

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `script` | string | Yes | JavaScript code to execute |

```python
result = aos_browser(
    action="evaluate",
    script="document.title",
    session_id="test-1"
)
```

**`get_cookies`** - Get all cookies

```python
cookies = aos_browser(action="get_cookies", session_id="test-1")
```

**`get_local_storage`** - Get local storage item

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `storage_key` | string | Yes | Local storage key |

```python
value = aos_browser(
    action="get_local_storage",
    storage_key="auth_token",
    session_id="test-1"
)
```

#### Interaction Actions

**`click`** - Click element

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `button` | string | No | Mouse button (`"left"`, `"right"`, `"middle"`) |
| `click_count` | integer | No | Number of clicks (1-3) |
| `modifiers` | array[string] | No | Keyboard modifiers (`["Alt", "Control", "Shift"]`) |

```python
aos_browser(
    action="click",
    selector="#submit-button",
    session_id="test-1"
)
```

**`type`** - Type text with keyboard

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `text` | string | Yes | Text to type |

```python
aos_browser(
    action="type",
    selector="#username",
    text="user@example.com",
    session_id="test-1"
)
```

**`fill`** - Fill input field

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `value` | string | Yes | Value to fill |

```python
aos_browser(
    action="fill",
    selector="#password",
    value="secret123",
    session_id="test-1"
)
```

**`select`** - Select dropdown option

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `value` | string | Yes | Option value to select |

```python
aos_browser(
    action="select",
    selector="#country",
    value="US",
    session_id="test-1"
)
```

#### Waiting Actions

**`wait`** - Wait for element state

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | CSS/XPath selector |
| `wait_for_state` | string | No | State (`"visible"`, `"hidden"`, `"attached"`, `"detached"`) |
| `wait_for_timeout` | integer | No | Timeout in ms (default: 30000) |

```python
aos_browser(
    action="wait",
    selector=".loading",
    wait_for_state="hidden",
    session_id="test-1"
)
```

#### Context Actions

**`emulate_media`** - Set color scheme/media features

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `color_scheme` | string | No | `"light"`, `"dark"`, `"no-preference"` |
| `reduced_motion` | string | No | `"reduce"`, `"no-preference"` |

```python
aos_browser(
    action="emulate_media",
    color_scheme="dark",
    session_id="test-1"
)
```

**`viewport`** - Resize browser viewport

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `viewport_width` | integer | Yes | Width in pixels |
| `viewport_height` | integer | Yes | Height in pixels |

```python
aos_browser(
    action="viewport",
    viewport_width=1920,
    viewport_height=1080,
    session_id="test-1"
)
```

**`set_cookies`** - Set cookies

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `cookies` | array[object] | Yes | Cookie objects with name, value, domain, path |

```python
aos_browser(
    action="set_cookies",
    cookies=[{
        "name": "session",
        "value": "abc123",
        "domain": "localhost",
        "path": "/"
    }],
    session_id="test-1"
)
```

#### Tab Management Actions

**`new_tab`** - Create new tab

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_tab_url` | string | No | URL for new tab |

```python
result = aos_browser(
    action="new_tab",
    new_tab_url="https://example.com",
    session_id="test-1"
)
# Returns: {"tab_id": "tab-uuid-2"}
```

**`switch_tab`** - Switch to tab by ID

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tab_id` | string | Yes | Tab identifier from `list_tabs` or `new_tab` |

```python
aos_browser(
    action="switch_tab",
    tab_id="tab-uuid-2",
    session_id="test-1"
)
```

**`close_tab`** - Close tab by ID

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tab_id` | string | Yes | Tab identifier |

```python
aos_browser(
    action="close_tab",
    tab_id="tab-uuid-2",
    session_id="test-1"
)
```

**`list_tabs`** - List all tabs

```python
result = aos_browser(action="list_tabs", session_id="test-1")
# Returns: {"tabs": [{"id": "tab-uuid-1", "active": true}, ...]}
```

#### File Operations Actions

**`upload_file`** - Upload file to input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `selector` | string | Yes | File input selector |
| `file_path` | string | Yes | Path to file to upload |

```python
aos_browser(
    action="upload_file",
    selector="#file-input",
    file_path="/path/to/file.pdf",
    session_id="test-1"
)
```

**`download_file`** - Download file from page

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `download_trigger_selector` | string | Yes | Selector to trigger download |
| `file_path` | string | No | Path to save file |

```python
aos_browser(
    action="download_file",
    download_trigger_selector="#download-button",
    file_path="/tmp/downloaded.zip",
    session_id="test-1"
)
```

#### Session Management Actions

**`close`** - Close session and release resources

```python
aos_browser(action="close", session_id="test-1")
```

#### Complete Example

```python
# Dark mode testing workflow
session_id = "dark-mode-test"

# Navigate
aos_browser(action="navigate", url="http://localhost:3000", session_id=session_id)

# Set dark mode
aos_browser(action="emulate_media", color_scheme="dark", session_id=session_id)

# Screenshot
aos_browser(
    action="screenshot",
    screenshot_path="/tmp/dark.png",
    screenshot_full_page=true,
    session_id=session_id
)

# Cleanup
aos_browser(action="close", session_id=session_id)
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `SessionNotFound` | Invalid `session_id` | Check session ID or create new session |
| `SelectorNotFound` | Element not found | Check selector is correct, wait for element to load |
| `NavigationTimeout` | Page didn't load in time | Increase `timeout` or check URL |
| `BrowserNotInstalled` | Playwright browser not installed | Run `playwright install chromium` |
| `ActionNotSupported` | Invalid `action` | Check action name is correct |

**Related:** None (standalone tool)

---

## Performance Guidelines

- **Tool Count:** Keep at most 20 tools enabled (selective loading)
- **RAG Queries:** Query once, implement from results
- **Workflow State:** Sessions persist across restarts
- **Browser Sessions:** Reuse sessions for test suites

---

## Troubleshooting

### Tool not found

Check enabled tool groups in `.agent-os/config.json`:
```json
{
  "enabled_tool_groups": ["rag", "workflow", "browser"]
}
```

### No results from search_standards

1. Check vector index exists: `.agent-os/.cache/vector_index/`
2. Wait 10-30s for file watcher rebuild
3. Use broader query terms

### Browser tool errors

1. Install Playwright: `pip install playwright && playwright install chromium`
2. Check browser manager initialized
3. Verify headless mode in CI/CD environments

---

## Related Documentation

- [Architecture](../explanation/architecture.md) - How MCP/RAG works
- [Workflows](./workflows.md) - Workflow system overview
- [Standards](./standards.md) - Universal standards indexed by RAG
