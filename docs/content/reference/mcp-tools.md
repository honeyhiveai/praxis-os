---
sidebar_position: 1
doc_type: reference
---

# MCP Tools Reference

Comprehensive API reference for prAxIs OS MCP (Model Context Protocol) tools.

## Overview

prAxIs OS provides unified, action-based tools for semantic search, workflow execution, browser automation, and file operations. Tools follow a consistent action-dispatch pattern for discoverability and ease of use.

**Available Tools:**
- `pos_search_project` - Unified search (6 actions across 4 indexes)
- `pos_workflow` - Workflow management (14 actions for lifecycle)
- `pos_browser` - Browser automation (24 actions for Playwright)
- `pos_filesystem` - File operations (12 actions for CRUD)
- `get_server_info` - Server status/health/metrics (4 actions)
- `current_date` - Current date/time (prevents date errors)

**Total:** 6 tools, ~60 actions

**Configuration:** Configure indexes and tools in `.praxis-os/config/mcp.yaml`:
```yaml
indexes:
  standards:
    enabled: true
  code:
    enabled: true
  ast:
    enabled: true
  graph:
    enabled: true
```

---

## Search Tools

### `pos_search_project`

Unified search tool for all project knowledge (standards, code, AST, call graphs).

**Purpose:** Single tool providing semantic search across multiple indexes. Find relevant chunks without reading entire files (90% context reduction per query). Drives query-first behavior that reduces overall messages by 71%.

**Actions:**
- `search_standards` - Hybrid search over standards documentation (vector + FTS + RRF + rerank)
- `search_code` - Semantic code search using CodeBERT embeddings
- `search_ast` - Structural AST search using Tree-sitter patterns
- `find_callers` - Graph traversal: who calls this symbol?
- `find_dependencies` - Graph traversal: what does this symbol call?
- `find_call_paths` - Graph traversal: show call chain between two symbols

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | One of: `search_standards`, `search_code`, `search_ast`, `find_callers`, `find_dependencies`, `find_call_paths` |
| `query` | string | Yes | Natural language question or symbol name |
| `method` | string | No | Search method: `hybrid` (default), `vector`, or `fts` |
| `n_results` | integer | No | Number of results to return (default: 5) |
| `max_depth` | integer | No | Max traversal depth for graph actions (default: 10) |
| `to_symbol` | string | No | Target symbol for `find_call_paths` (required for that action) |
| `filters` | dict | No | Metadata filters (e.g., `{"domain": "workflow", "phase": 3, "tags": ["async"]}`) |

**Returns:** `Dict[str, Any]` - Search results with content chunks, file paths, and relevance scores.

```python
{
  "status": "success",
  "action": "search_standards",
  "results": [
    {
      "content": "Chunk content...",
      "file": "standards/concurrency/race-conditions.md",
      "section": "Detection Strategies",
      "relevance_score": 0.89,
      "tokens": 156
    }
  ],
  "count": 5,
  "metadata": {
    "total_tokens": 753,
    "retrieval_method": "hybrid",
    "query_time_ms": 132.8
  }
}
```

**Examples:**

```python
# Search standards docs
pos_search_project(
    action="search_standards",
    query="How does the workflow system work?",
    n_results=5
)

# Search code semantically
pos_search_project(
    action="search_code",
    query="authentication middleware",
    n_results=5
)

# Find who calls a function
pos_search_project(
    action="find_callers",
    query="process_workflow_phase",
    max_depth=5
)

# Find call path between two functions
pos_search_project(
    action="find_call_paths",
    query="start_workflow",
    to_symbol="execute_phase",
    max_depth=10
)
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `No results found` | Query too specific or no indexed content | Broaden query terms, check `.praxis-os/cache/indexes/` exists |
| `Index not found` | RAG not initialized | Wait 10-30s for file watcher to build index |
| `Invalid action` | Unknown action parameter | Use valid action from list above |

**Related:** [pos_workflow](#pos_workflow), [current_date](#current_date)

---

### `current_date`

Get current date and time for preventing date errors in AI-generated content.

**Purpose:** AI assistants frequently make date mistakes (using wrong dates, inconsistent formats). This tool provides the reliable current date/time that should be used for creating specifications, generating directory names with timestamps, adding date headers to documentation, and any content requiring accurate current date.

**Parameters:** None

**Returns:** `Dict[str, Any]` - Current date in multiple formats.

```python
{
  "iso_date": "2025-11-06",
  "iso_datetime": "2025-11-06T22:30:00.123456",
  "day_of_week": "Wednesday",
  "month": "November",
  "year": 2025,
  "unix_timestamp": 1728768600,
  "formatted": {
    "spec_directory": "2025-11-06-",
    "header": "**Date**: 2025-11-06",
    "full_readable": "Wednesday, November 6, 2025"
  },
  "usage_note": "Use iso_date for file names, iso_datetime for timestamps"
}
```

**Examples:**

```python
# Get current date for spec directory
date_info = current_date()
spec_dir = f".praxis-os/specs/{date_info['iso_date']}-my-feature"

# Use in documentation header
header = f"# Feature Spec\n{date_info['formatted']['header']}\n"
```

**Errors:** None (always succeeds)

**Related:** [pos_search_project](#pos_search_project)

---

## Workflow Tools

### `pos_workflow`

Unified workflow management tool using action-based dispatch.

**Purpose:** Single unified interface for all workflow operations - discovery, execution, management, and recovery.

**Actions:**

#### Discovery (1 action)
- `list_workflows` - List available workflows with optional category filtering

#### Execution (5 actions)
- `start` - Start new workflow session
- `get_phase` - Get current phase content
- `get_task` - Get specific task details
- `complete_phase` - Submit evidence and complete phase
- `get_state` - Get complete workflow state

#### Management (3 actions)
- `list_sessions` - List all workflow sessions
- `get_session` - Get session details
- `delete_session` - Delete workflow session

#### Recovery (5 actions)
- `pause` - Pause workflow session
- `resume` - Resume paused workflow session
- `retry_phase` - Retry failed phase
- `rollback` - Rollback to previous phase
- `get_errors` - Get errors for failed session

**Common Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Operation to perform (see actions above) |
| `session_id` | string | Conditional | Session identifier (required for most operations) |
| `workflow_type` | string | Conditional | Workflow type (required for `start`) |
| `target_file` | string | Conditional | Target file path (required for `start`) |
| `options` | dict/string | No | Optional workflow configuration (for `start`) |
| `phase` | integer | Conditional | Phase number (for `get_task`, `complete_phase`, `retry_phase`) |
| `task_number` | integer | Conditional | Task number (for `get_task`) |
| `evidence` | dict | Conditional | Evidence dictionary (required for `complete_phase`) |
| `category` | string | No | Workflow category filter (for `list_workflows`) |
| `status` | string | No | Session status filter (for `list_sessions`) |
| `reason` | string | No | Pause/resume reason (for `pause`, `resume`) |
| `checkpoint_note` | string | No | Note for pause checkpoint (for `pause`) |
| `reset_evidence` | boolean | No | Reset evidence on retry (for `retry_phase`) |
| `to_phase` | integer | No | Target phase for rollback (for `rollback`) |

**Examples:**

```python
# Start a workflow
pos_workflow(
    action="start",
    workflow_type="spec_execution_v1",
    target_file="specs/ouroboros.md"
)

# Get current phase
pos_workflow(
    action="get_phase",
    session_id="550e8400-..."
)

# Complete phase with evidence
pos_workflow(
    action="complete_phase",
    session_id="550e8400-...",
    phase=1,
    evidence={"tests_passed": 15, "coverage": 95}
)

# List all workflows
pos_workflow(action="list_workflows")

# List active sessions
pos_workflow(action="list_sessions", status="active")
```

**Returns:** Action-specific response dictionary with `status`, `action`, and result data.

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `Unknown action` | Invalid `action` parameter | Use valid action from list above |
| `SessionNotFound` | Invalid `session_id` | Check session ID or start new workflow |
| `Invalid session_id format` | Malformed UUID | Provide valid UUID format |
| `directory traversal detected` | Security violation in `target_file` | Use relative paths only |
| `Evidence too large` | Evidence exceeds 10MB limit | Reduce evidence payload size |

**Related:** [pos_browser](#pos_browser), [pos_filesystem](#pos_filesystem)

---

## Browser Tools

### `pos_browser`

Comprehensive browser automation with Playwright.

**Purpose:** Browser testing, automation, and inspection with persistent sessions.

**Actions:**

#### Navigation (1 action)
- `navigate` - Navigate to URL

#### Inspection (6 actions)
- `screenshot` - Capture page screenshot
- `console` - Get console messages
- `query` - Query elements by selector
- `evaluate` - Execute JavaScript
- `get_cookies` - Get all cookies
- `get_local_storage` - Get local storage item

#### Interaction (4 actions)
- `click` - Click element
- `type` - Type text with keyboard
- `fill` - Fill input field
- `select` - Select dropdown option

#### Waiting (1 action)
- `wait` - Wait for element state

#### Context (3 actions)
- `emulate_media` - Set color scheme/media features
- `viewport` - Resize browser viewport
- `set_cookies` - Set cookies

#### Advanced (9 actions)
- `run_test` - Execute Playwright test script
- `intercept_network` - Intercept/mock network requests
- `new_tab` - Create new tab
- `switch_tab` - Switch to tab by ID
- `close_tab` - Close tab by ID
- `list_tabs` - List all tabs
- `upload_file` - Upload file to input
- `download_file` - Download file from page
- `close` - Close session and release resources

**Common Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform (see actions above) |
| `session_id` | string | No | Session identifier for isolation |
| `browser_type` | string | No | Browser (`chromium`, `firefox`, `webkit`) (default: `chromium`) |
| `headless` | boolean | No | Run headless (default: `true`) |
| `timeout` | integer | No | Operation timeout in ms (default: 30000) |
| `url` | string | Conditional | Target URL (for `navigate`) |
| `selector` | string | Conditional | CSS/XPath selector (for `query`, `click`, etc.) |
| `text` | string | Conditional | Text to type (for `type`) |
| `value` | string | Conditional | Value to fill/select (for `fill`, `select`) |
| `screenshot_path` | string | Conditional | File path to save screenshot (for `screenshot`) |
| `script` | string | Conditional | JavaScript to execute (for `evaluate`) |
| `cookies` | list | Conditional | Cookies to set (for `set_cookies`) |
| `file_path` | string | Conditional | Path to file for upload/download |

**Examples:**

```python
# Navigate to URL
pos_browser(
    action="navigate",
    url="https://example.com",
    session_id="test-1"
)

# Take screenshot
pos_browser(
    action="screenshot",
    screenshot_path="/tmp/page.png",
    screenshot_full_page=True,
    session_id="test-1"
)

# Click element
pos_browser(
    action="click",
    selector="#submit-button",
    session_id="test-1"
)
```

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `SessionNotFound` | Invalid `session_id` | Check session ID or create new session |
| `SelectorNotFound` | Element not found | Check selector is correct, wait for element to load |
| `NavigationTimeout` | Page didn't load in time | Increase `timeout` or check URL |
| `BrowserNotInstalled` | Playwright browser not installed | Run `playwright install chromium` |

**Related:** [pos_filesystem](#pos_filesystem)

---

## Filesystem Tools

### `pos_filesystem`

Unified file operations with safe defaults.

**Purpose:** Provides comprehensive filesystem operations with security validation:
- Path traversal prevention (no "..", no absolute paths outside workspace)
- Gitignore respect (won't modify ignored files without override)
- Safe defaults (no recursive delete without explicit flag)
- Actionable error messages with remediation guidance

**Actions:**

#### Content Operations (3 actions)
- `read` - Read file contents (encoding configurable)
- `write` - Write content to file (creates if not exists)
- `append` - Append content to file (creates if not exists)

#### File Management (3 actions)
- `delete` - Delete file or directory (requires recursive=True for dirs)
- `move` - Move/rename file or directory
- `copy` - Copy file or directory

#### Discovery (4 actions)
- `list` - List directory contents (recursive optional)
- `exists` - Check if path exists
- `stat` - Get file/directory metadata (size, modified time, etc.)
- `glob` - Search for files matching pattern

#### Directory Operations (2 actions)
- `mkdir` - Create directory (create_parents for nested dirs)
- `rmdir` - Remove empty directory

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | File operation to perform (required) |
| `path` | string | Yes | File or directory path (required, relative to workspace) |
| `content` | string | Conditional | Content to write/append (for `write`, `append`) |
| `destination` | string | Conditional | Destination path (for `move`, `copy`) |
| `recursive` | boolean | No | Enable recursive operations (delete dirs, list subdirs) |
| `follow_symlinks` | boolean | No | Follow symbolic links |
| `encoding` | string | No | Text encoding (default: utf-8) |
| `create_parents` | boolean | No | Create parent directories if needed (`mkdir`, `write`) |
| `override_gitignore` | boolean | No | Allow operations on gitignored files |

**Examples:**

```python
# Read file
pos_filesystem(
    action="read",
    path="src/module.py"
)

# Write file with parent creation
pos_filesystem(
    action="write",
    path="output/results.txt",
    content="Hello, World!",
    create_parents=True
)

# List directory recursively
pos_filesystem(
    action="list",
    path="src/",
    recursive=True
)

# Delete directory (requires recursive flag)
pos_filesystem(
    action="delete",
    path="tmp/",
    recursive=True
)
```

**Returns:** Dictionary with `status`, `action`, `path`, and action-specific result data.

**Errors:**

| Error | Cause | Solution |
|-------|-------|----------|
| `PathTraversalError` | Path contains ".." or absolute path | Use relative paths within workspace |
| `GitignoreViolation` | Attempting to modify gitignored file | Set `override_gitignore=True` if intentional |
| `FileNotFound` | Path doesn't exist | Check path is correct |
| `DirectoryNotEmpty` | Attempting to delete non-empty directory | Set `recursive=True` |

**Related:** [pos_browser](#pos_browser)

---

## Server Information Tools

### `get_server_info`

Get server and project information for observability.

**Purpose:** Provides comprehensive server metadata, health status, behavioral metrics, and version information for monitoring, debugging, and observing AI improvement.

**Actions:**
- `status` - Server runtime (uptime, config, subsystems initialized)
- `health` - Index health status, parsers installed, config validation
- `behavioral_metrics` - Query frequency, diversity, trends (from query_tracker)
- `version` - Server version, Python version, key dependencies

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | No | Information type to retrieve (default: `status`) |

**Returns:** Dictionary with `status`, `action`, and action-specific information.

**Examples:**

```python
# Get server status
get_server_info(action="status")

# Check index health
get_server_info(action="health")

# View behavioral metrics
get_server_info(action="behavioral_metrics")

# Get version info
get_server_info(action="version")
```

**Errors:** None (always succeeds)

**Related:** [pos_search_project](#pos_search_project)

---

## Performance Guidelines

- **Tool Count:** prAxIs OS provides 6 unified tools (~60 actions total)
- **RAG Queries:** Query once, implement from results
- **Workflow State:** Sessions persist across restarts
- **Browser Sessions:** Reuse sessions for test suites
- **File Operations:** Use `pos_filesystem` instead of direct file reads

---

## Troubleshooting

### Tool not found

Check that MCP server is running and tools are registered:
```bash
# Check server status
get_server_info(action="status")

# Verify tools available
# (Check in your IDE's MCP tools list)
```

### No results from pos_search_project

1. Check vector index exists: `.praxis-os/cache/indexes/`
2. Wait 10-30s for file watcher rebuild
3. Use broader query terms
4. Verify index is enabled in `mcp.yaml`

### Browser tool errors

1. Install Playwright: `pip install playwright && playwright install chromium`
2. Check browser manager initialized
3. Verify headless mode in CI/CD environments

### Filesystem tool errors

1. Verify path is relative to workspace root
2. Check `.gitignore` if operation fails (may need `override_gitignore=True`)
3. Ensure `recursive=True` for directory deletion

---

## Related Documentation

- [Architecture](../explanation/architecture.md) - How MCP/RAG works
- [Workflows](./workflows.md) - Workflow system overview
- [Standards](./standards.md) - Universal standards indexed by RAG
- [Agent Integrations](../how-to-guides/agent-integrations/README.md) - Setup guides for each agent
