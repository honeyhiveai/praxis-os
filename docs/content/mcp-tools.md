---
sidebar_position: 7
---

# MCP Tools Reference

Agent OS Enhanced provides a comprehensive set of MCP (Model Context Protocol) tools for AI agents. These tools enable semantic search, workflow management, and browser automation.

## Tool Groups

Tools are organized into groups for selective loading:

- **`rag`**: Semantic search over standards and documentation
- **`workflow`**: Workflow execution with architectural phase gating
- **`browser`**: Browser automation with Playwright

## Configuration

Enable/disable tool groups in `.agent-os/config.json`:

```json
{
  "enabled_tool_groups": ["rag", "workflow", "browser"]
}
```

:::tip Performance
Research shows LLM performance degrades by up to 85% with >20 tools. Agent OS uses selective loading to stay within optimal limits.
:::

---

## RAG Tools

### `search_standards`

Semantic search over universal standards, usage guides, and workflow documentation.

**Purpose**: Find relevant documentation chunks without reading entire files (90% context reduction).

**Parameters**:
- `query` (string, required): Natural language question
- `n_results` (integer, optional): Number of results to return (default: 5)
- `filter_phase` (integer, optional): Filter by workflow phase number (1-8)
- `filter_tags` (array, optional): Filter by tags (e.g., `["testing", "concurrency"]`)

**Returns**:
```json
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

**Example**:
```python
# Query MCP before implementing
result = search_standards(
    query="How do I handle race conditions in shared state?",
    n_results=3
)
```

**Benefits**:
- 2-5KB targeted chunks vs 50KB files
- 24x better relevance (4% → 95% relevant content)
- 95% token reduction (12,500 → 625 tokens)

---

## Workflow Tools

### `start_workflow`

Initialize a new workflow session with phase gating enforcement.

**Parameters**:
- `workflow_type` (string, required): Workflow identifier (e.g., `"spec_creation_v1"`)
- `target_file` (string, required): File being worked on
- `options` (object, optional): Workflow-specific configuration

**Returns**:
```json
{
  "session_id": "ed5481fe-7334-427c-bea4-c8e6103a592b",
  "workflow_type": "spec_creation_v1",
  "current_phase": 1,
  "phase_content": {
    "title": "Phase 1: Problem Analysis",
    "objectives": [...],
    "commands": [...],
    "deliverables": [...]
  },
  "acknowledgment_required": true
}
```

**Example**:
```python
session = start_workflow(
    workflow_type="spec_creation_v1",
    target_file="config/database.py"
)
```

---

### `get_current_phase`

Retrieve content and requirements for the current workflow phase.

**Parameters**:
- `session_id` (string, required): Workflow session identifier

**Returns**:
```json
{
  "session_id": "ed5481fe...",
  "current_phase": 2,
  "phase_content": {
    "title": "Phase 2: Solution Design",
    "objectives": [...],
    "commands": [...],
    "deliverables": [...]
  },
  "artifacts": {
    "phase_1": {
      "problem_statement": "...",
      "requirements": [...]
    }
  }
}
```

---

### `get_task`

Get complete content for a specific task (horizontal scaling).

**Parameters**:
- `session_id` (string, required): Workflow session identifier
- `phase` (integer, required): Phase number
- `task_number` (integer, required): Task number within phase

**Returns**:
```json
{
  "session_id": "ed5481fe...",
  "phase": 2,
  "task_number": 1,
  "task_content": {
    "title": "Design Data Model",
    "description": "...",
    "steps": [...],
    "commands": [...],
    "validation": [...]
  }
}
```

**Meta-Framework Principle**: Work on one task at a time.

---

### `complete_phase`

Submit evidence and attempt phase completion with validation.

**Parameters**:
- `session_id` (string, required): Workflow session identifier
- `phase` (integer, required): Phase number being completed
- `evidence` (object, required): Evidence matching checkpoint criteria

**Returns** (if passed):
```json
{
  "status": "passed",
  "phase_completed": 2,
  "next_phase": 3,
  "next_phase_content": {
    "title": "Phase 3: Implementation",
    ...
  }
}
```

**Returns** (if failed):
```json
{
  "status": "failed",
  "missing_evidence": ["srd.md", "architectural_diagram"],
  "current_phase_content": {...}
}
```

**Architectural Gating**: AI **cannot** skip phases or bypass quality gates.

---

### `get_workflow_state`

Get complete workflow state for debugging or resume.

**Parameters**:
- `session_id` (string, required): Workflow session identifier

**Returns**:
```json
{
  "session_id": "ed5481fe...",
  "workflow_type": "spec_creation_v1",
  "current_phase": 3,
  "completed_phases": [1, 2],
  "artifacts": {...},
  "can_resume": true,
  "state_file": ".agent-os/state/ed5481fe....json"
}
```

**Persistent State**: Survives MCP server restarts.

---

### `create_workflow`

Generate new AI-assisted workflow framework using meta-framework principles.

**Parameters**:
- `name` (string, required): Framework name (e.g., `"api-documentation"`)
- `workflow_type` (string, required): Type (e.g., `"documentation"`, `"testing"`)
- `phases` (array, required): Phase names (e.g., `["Analysis", "Generation", "Validation"]`)
- `target_language` (string, optional): Programming language (default: `"python"`)
- `quick_start` (boolean, optional): Use minimal template (default: `true`)
- `output_path` (string, optional): Custom output path

**Returns**:
```json
{
  "workflow_name": "api-documentation",
  "phases": 3,
  "files_created": [
    ".agent-os/workflows/api-documentation/metadata.json",
    ".agent-os/workflows/api-documentation/phases/phase_1.md",
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

---

### `validate_workflow`

Validate workflow structure against construction standards.

**Parameters**:
- `workflow_path` (string, required): Path to workflow directory (e.g., `"universal/workflows/my_workflow_v1"`)

**Returns**:
```json
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

**Validates**:
- Standard directory structure (`phases/N/phase.md` + `task-N-name.md`)
- File naming conventions (`phase.md` not `README.md`)
- File size guidelines (phase ~80 lines, tasks 100-170 lines)
- Required `metadata.json` presence and validity

**Example**:
```python
# Validate before committing
result = validate_workflow(
    workflow_path=".agent-os/workflows/my_custom_workflow_v1"
)

if result["compliant"]:
    print("Ready to commit!")
else:
    print("Issues found:", result["issues"])
```

---

### `current_date`

Get current date and time for preventing date errors in AI-generated content.

**Purpose**: AI assistants frequently make date mistakes (using wrong dates, inconsistent formats). This tool provides reliable current date/time for:
- Creating specifications with correct dates
- Generating directory names with timestamps
- Adding date headers to documentation
- Any content requiring accurate current date

**Parameters**: None

**Returns**:
```json
{
  "iso_date": "2025-10-08",
  "iso_datetime": "2025-10-08T14:30:00.123456",
  "day_of_week": "Tuesday",
  "month": "October",
  "year": 2025,
  "unix_timestamp": 1728398400,
  "formatted": {
    "spec_directory": "2025-10-08-",
    "header": "**Date**: 2025-10-08",
    "full_readable": "Tuesday, October 8, 2025"
  },
  "usage_note": "Use 'iso_date' for specs and documentation headers..."
}
```

**Example**:
```python
# Get current date for spec creation
date_info = current_date()

# Use in spec directory name
spec_dir = f".agent-os/specs/{date_info['iso_date']}-my-feature"

# Use in documentation header
header = f"# Feature Spec\n{date_info['formatted']['header']}\n"
```

**Why This Tool Exists**: Without it, AI agents often use:
- Yesterday's date (cached context)
- Random dates from training data
- Inconsistent formats (MM-DD-YYYY vs YYYY-MM-DD)

---

## Browser Tools

### `aos_browser`

Comprehensive browser automation with Playwright.

**Actions**:

#### Navigation
- **`navigate`**: Navigate to URL
  - `url` (string): Target URL
  - `wait_until` (string): Wait condition (`"load"`, `"domcontentloaded"`, `"networkidle"`)
  - `timeout` (integer): Timeout in milliseconds (default: 30000)

#### Inspection
- **`screenshot`**: Capture page screenshot
  - `screenshot_path` (string): File path to save
  - `screenshot_full_page` (boolean): Capture full scrollable page
  - `screenshot_format` (string): Format (`"png"`, `"jpeg"`)

- **`query`**: Query elements by selector
  - `selector` (string): CSS/XPath selector
  - `query_all` (boolean): Return all matches vs first

- **`evaluate`**: Execute JavaScript
  - `script` (string): JavaScript code to execute

- **`get_cookies`**: Get all cookies

- **`get_local_storage`**: Get local storage item
  - `storage_key` (string): Storage key

#### Interaction
- **`click`**: Click element
  - `selector` (string): CSS/XPath selector
  - `button` (string): Mouse button (`"left"`, `"right"`, `"middle"`)
  - `click_count` (integer): Number of clicks (1-3)
  - `modifiers` (array): Keyboard modifiers (`["Alt", "Control", "Meta", "Shift"]`)

- **`type`**: Type text with keyboard
  - `selector` (string): CSS/XPath selector
  - `text` (string): Text to type

- **`fill`**: Fill input field
  - `selector` (string): CSS/XPath selector
  - `value` (string): Value to fill

- **`select`**: Select dropdown option
  - `selector` (string): CSS/XPath selector
  - `value` (string): Option value to select

#### Waiting
- **`wait`**: Wait for element state
  - `selector` (string): CSS/XPath selector
  - `wait_for_state` (string): State (`"visible"`, `"hidden"`, `"attached"`, `"detached"`)
  - `wait_for_timeout` (integer): Timeout in milliseconds

#### Context
- **`emulate_media`**: Set color scheme/media features
  - `color_scheme` (string): `"light"`, `"dark"`, `"no-preference"`
  - `reduced_motion` (string): `"reduce"`, `"no-preference"`

- **`viewport`**: Resize browser viewport
  - `viewport_width` (integer): Width in pixels
  - `viewport_height` (integer): Height in pixels

- **`set_cookies`**: Set cookies
  - `cookies` (array): Cookie objects

#### Tab Management
- **`new_tab`**: Create new tab
  - `new_tab_url` (string, optional): URL for new tab

- **`switch_tab`**: Switch to tab by ID
  - `tab_id` (string): Tab identifier

- **`close_tab`**: Close tab by ID
  - `tab_id` (string): Tab identifier

- **`list_tabs`**: List all tabs

#### File Operations
- **`upload_file`**: Upload file to input
  - `selector` (string): File input selector
  - `file_path` (string): Path to file

- **`download_file`**: Download file from page
  - `download_trigger_selector` (string): Selector to trigger download
  - `file_path` (string, optional): Path to save file

#### Session Management
- **`close`**: Close session and release resources

**Global Parameters**:
- `session_id` (string, optional): Session identifier for isolation
- `browser_type` (string): Browser (`"chromium"`, `"firefox"`, `"webkit"`)
- `headless` (boolean): Run in headless mode

**Example - Test Dark Mode**:
```python
# Navigate
aos_browser(
    action="navigate",
    url="http://localhost:3000",
    session_id="dark-mode-test"
)

# Set dark mode
aos_browser(
    action="emulate_media",
    color_scheme="dark",
    session_id="dark-mode-test"
)

# Capture screenshot
aos_browser(
    action="screenshot",
    screenshot_path="/tmp/dark-mode.png",
    screenshot_full_page=True,
    session_id="dark-mode-test"
)

# Cleanup
aos_browser(
    action="close",
    session_id="dark-mode-test"
)
```

**Example - Tab Management**:
```python
# List tabs
result = aos_browser(action="list_tabs", session_id="test")
# Returns: {"tabs": [{"id": "tab-uuid-1", "active": true}]}

# Create new tab
aos_browser(
    action="new_tab",
    new_tab_url="https://docs.honeyhive.ai",
    session_id="test"
)

# Switch to specific tab
aos_browser(
    action="switch_tab",
    tab_id="tab-uuid-2",
    session_id="test"
)

# Close tab
aos_browser(
    action="close_tab",
    tab_id="tab-uuid-1",
    session_id="test"
)
```

**Session Isolation**:
- Each `session_id` gets isolated browser process
- Sessions persist state (cookies, localStorage)
- Sessions survive MCP server restarts
- Multi-chat safety (different agents can't interfere)

---

## Best Practices

### Query MCP Before Implementation

```python
# ❌ BAD: Guess at implementation
def handle_race_condition():
    # Hope this works...
    pass

# ✅ GOOD: Query standards first
result = search_standards(
    query="How do I handle race conditions with shared state?",
    n_results=3
)
# Implement based on precise guidance
```

### Use Workflows for Complex Tasks

```python
# Start workflow
session = start_workflow(
    workflow_type="spec_creation_v1",
    target_file="api/endpoints.py"
)

# Follow phase-by-phase
phase1 = get_current_phase(session_id=session["session_id"])
# Complete phase 1...

# Submit evidence
complete_phase(
    session_id=session["session_id"],
    phase=1,
    evidence={
        "problem_statement": "...",
        "requirements": [...]
    }
)
```

### Browser Testing with Sessions

```python
# Persistent session for test suite
session_id = "integration-tests"

# Test 1: Homepage
aos_browser(action="navigate", url="/", session_id=session_id)
aos_browser(action="screenshot", screenshot_path="/tmp/home.png", session_id=session_id)

# Test 2: Login (session persists)
aos_browser(action="navigate", url="/login", session_id=session_id)
aos_browser(action="fill", selector="#username", value="test@example.com", session_id=session_id)

# Cleanup
aos_browser(action="close", session_id=session_id)
```

---

## Performance Guidelines

1. **Tool Count**: Keep ≤20 tools enabled (use selective loading)
2. **RAG Queries**: Query once, implement from results (don't re-query)
3. **Workflow State**: Sessions persist across restarts (no re-initialization)
4. **Browser Sessions**: Reuse sessions for test suites (avoid repeated setup)

---

## Troubleshooting

### "Tool not found"

Check enabled tool groups in `.agent-os/config.json`:
```json
{
  "enabled_tool_groups": ["rag", "workflow", "browser"]
}
```

### "No results from search_standards"

1. Check if standards are indexed: Look for `.agent-os/.cache/vector_index/`
2. Wait for file watcher rebuild (10-30 seconds after content changes)
3. Try broader query terms

### Browser tool errors

1. Ensure Playwright is installed: `pip install playwright && playwright install chromium`
2. Check browser_manager is initialized
3. Verify headless mode if running in CI/CD

---

## Related Documentation

- [Architecture](./architecture.md) - How MCP/RAG works
- [Workflows](./workflows.md) - Workflow system overview
- [Standards](./standards.md) - Universal standards indexed by RAG

