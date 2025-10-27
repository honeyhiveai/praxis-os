# pos_filesystem Tool Design Document

**Date**: 2025-10-25  
**Status**: Phase 1 - Design (Awaiting Human Review)  
**Author**: AI Agent (Cursor/Claude)

---

## Problem Statement

### What are we solving?

Sub-agents (specialist personas launched via PersonaLauncher) need to perform file I/O operations to complete their tasks:

**Current Pain Points:**
1. **No file access for sub-agents** - Specialists can't write analysis documents, read project files, or create deliverables
2. **Main agent dependency** - Every file operation requires main agent intervention, breaking autonomy
3. **Missing primitive** - File I/O is a fundamental OS capability, currently absent from "Agent OS"

**Impact if not solved:**
- Sub-agents can only provide advisory text (via return values)
- Cannot create deliverables (specs, analysis docs, code files)
- Cannot read project context independently
- "Dev team in a box" vision blocked

**Scope Boundaries:**
- **In Scope**: Basic file I/O for sub-agents (read, write, list, delete, exists, mkdir)
- **Out of Scope**: Advanced features (search, copy, move, symlinks, permissions, binary files)
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Safety**: Workspace-sandboxed, validated paths, structured returns

**Success looks like:**
A database specialist sub-agent can independently:
1. Read existing schema files
2. Write a comprehensive analysis document
3. Create directory structure for deliverables
4. Check if files exist before operations
5. All operations sandboxed to project workspace

---

## Goals & Non-Goals

### Goals (In Scope)

1. **Enable Sub-Agent File I/O** - Provide safe, sandboxed file operations for PersonaLauncher sub-agents
2. **Cross-Platform Safety** - Pure Python implementation works on Windows/macOS/Linux without shell dependencies
3. **Workspace Sandboxing** - All paths validated and confined to project root (no directory traversal)
4. **Structured Returns** - JSON-serializable responses with success/error details
5. **Unix-Inspired Implementation** - Learn from sed/grep/tail algorithms for robust file handling
6. **Domain Consolidation** - Single `pos_filesystem` tool with action dispatch (consistent with `pos_workflow`, `pos_browser`)
7. **Partial Read Support** - Efficient reading of file ranges (inspired by Cursor and CrewAI patterns)
8. **Type Safety** - MCP schema validation for all parameters

### Non-Goals (Out of Scope)

1. **Shell Access** - No `pos_shell` or terminal command execution (security risk)
2. **Advanced Text Processing** - No regex search, no sed-like editing (can be composed from read+write)
3. **File Operations** - No copy, move, symlink operations (future, if needed)
4. **Binary File Support** - Text files only (UTF-8 encoding) in MVP
5. **Permission Management** - No chmod, chown operations
6. **Approval Flow** - No user approval UI (different from main agent tools like Cursor's read_file)
7. **Multi-Format Support** - No special handling for images, PDFs, notebooks (future: pos_notebook, pos_image)
8. **File Watching** - No real-time file change notifications

---

## Current State Analysis

### What exists today?

**Main Agent Tools (Cursor provides):**
- `read_file(path, offset?, limit?)` - Partial read support
- `write(path, content)` - Create/overwrite
- `search_replace(path, old, new, replace_all?)` - Targeted edits
- `delete_file(path)` - File deletion
- `list_dir(path, ignore_globs?)` - Directory listing
- `glob_file_search(pattern, target?)` - Pattern-based discovery

**Sub-Agent Tools (Currently available via PersonaLauncher):**
1. `search_standards` - RAG search
2. `pos_workflow` - Workflow operations
3. `pos_browser` - Web automation
4. `get_server_info` - Server info
5. `current_date` - Date/time

**Missing:** File I/O operations for sub-agents

### What works well (keep this)

✅ **Main agent has full file access** - Read, write, edit patterns work well
✅ **Domain consolidation** - `pos_workflow` and `pos_browser` use action dispatch successfully
✅ **Partial reads** - Cursor's offset/limit pattern is essential for large files
✅ **Sandboxing** - Main agent tools validate paths (we should inherit this)
✅ **Structured returns** - JSON responses work better than text streams

### What's broken (fix this)

❌ **Sub-agents have no file I/O** - Cannot write deliverables or read context
❌ **No filesystem primitive in Agent OS** - Missing fundamental OS capability
❌ **Manual composition only** - Main agent must orchestrate all file operations for sub-agents

### What's missing (add this)

🔨 **pos_filesystem tool** - File I/O primitive for sub-agents
🔨 **Workspace sandboxing** - Path validation and confinement
🔨 **tools/list exposure** - Sub-agents need to discover file operations dynamically
🔨 **Usage patterns documented** - Standards teach composition (append = read + write)

### Metrics/Data Supporting Need

**From research (5 agent frameworks analyzed):**
- 100% of agents provide file read/write (Cline, LangChain, AutoGPT, CrewAI, Cursor)
- 80% provide directory listing (4 out of 5)
- 67% provide partial read support (Cursor, CrewAI, Claude Code)
- 60% provide delete operations (3 out of 5)
- 40% provide separate edit operations (2 out of 5)

**Tool count pattern:**
- All frameworks: 2-7 file tools
- Average: ~6 file tools
- None use action-based consolidation (but none have Agent OS's constraints)

---

## Proposed Design

### Architecture

```
┌─────────────────────────────────────────┐
│ Sub-Agent (Database Specialist)         │
├─────────────────────────────────────────┤
│                                         │
│ Needs file I/O:                         │
│   pos_filesystem(action="write", ...)   │
│                      │                  │
└──────────────────────┼──────────────────┘
                       │ MCP Call
                       ▼
┌─────────────────────────────────────────┐
│ MCP Server Process                      │
├─────────────────────────────────────────┤
│                                         │
│ @mcp.tool()                             │
│ async def pos_filesystem(               │
│     action: Literal[...],               │
│     path: str,                          │
│     **kwargs                            │
│ ) -> Dict[str, Any]:                    │
│                                         │
│     # Validate path (sandbox)           │
│     validated = validate_path(path)     │
│                                         │
│     # Dispatch to implementation        │
│     match action:                       │
│         case "read": return _read(...)  │
│         case "write": return _write(..) │
│         # ...                           │
│                                         │
└─────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────┐
│ Implementation Layer (Unix Philosophy)  │
├─────────────────────────────────────────┤
│                                         │
│ operations/                             │
│ ├── read.py                             │
│ │   def _read_file(path, start, count) │
│ │   # Inspired by: cat, head, tail     │
│ │   # - Efficient partial reads        │
│ │   # - Binary detection              │
│ │                                      │
│ ├── write.py                            │
│ │   def _write_file(path, content)     │
│ │   # Inspired by: sed -i, cp          │
│ │   # - Safe temp file usage           │
│ │   # - Atomic operations             │
│ │                                      │
│ ├── list.py                             │
│ │   def _list_directory(path)          │
│ │   # Inspired by: ls, find            │
│ │                                      │
│ └── [delete, exists, mkdir].py          │
│                                         │
└─────────────────────────────────────────┘
```

### Data Models

#### MCP Tool Input Schema

```python
# Action-based dispatch (consolidated)
{
    "action": Literal[
        "read",      # Read file (full or partial)
        "write",     # Create or overwrite file
        "list",      # List directory contents
        "delete",    # Delete file
        "exists",    # Check if path exists
        "mkdir"      # Create directory
    ],
    
    # Core parameters
    "path": str,                          # Required: relative path from project root
    "content": Optional[str] = None,      # For write action
    
    # Partial read parameters (Cursor/CrewAI pattern)
    "start_line": Optional[int] = None,   # 1-indexed line number
    "line_count": Optional[int] = None,   # Number of lines to read
    
    # Safety parameters
    "encoding": str = "utf-8",            # File encoding
    "max_size_mb": int = 10,              # Safety limit for read
    "create_dirs": bool = True            # Auto-create parent dirs
}
```

#### MCP Tool Output Schema

```python
# Consistent return structure
{
    "success": bool,                    # Operation succeeded?
    "action": str,                      # Echo the action performed
    "path": str,                        # Echo the path operated on
    "message": str,                     # Human-readable result
    
    # Action-specific fields (optional)
    "content": Optional[str],           # For read action
    "exists": Optional[bool],           # For exists action
    "entries": Optional[List[str]],     # For list action
    "size_bytes": Optional[int],        # For read/write actions
    "lines": Optional[int],             # For read action
    
    # Error details (if success=False)
    "error": Optional[str],             # Error message
    "error_type": Optional[str]         # FileNotFoundError, PermissionError, etc.
}
```

### Key Behaviors

#### 1. Path Validation & Sandboxing

```python
def validate_path(path: str, project_root: Path) -> Path:
    """
    Validate and sandbox path to project workspace.
    
    Prevents:
    - Directory traversal (../../etc/passwd)
    - Absolute paths escaping workspace
    - Hidden file access (configurable)
    
    Inspired by: All agent frameworks use similar validation
    """
    # Remove leading slash, resolve relative to project root
    clean_path = path.lstrip("/")
    resolved = (project_root / clean_path).resolve()
    
    # Ensure path is within project root
    if not str(resolved).startswith(str(project_root)):
        raise ValueError(
            f"Path traversal detected: {path} resolves outside workspace"
        )
    
    return resolved
```

#### 2. Partial File Reading

```python
def _read_file_partial(
    path: Path,
    start_line: int,
    line_count: Optional[int]
) -> str:
    """
    Read file range efficiently.
    
    Inspired by: tail -n +100 file | head -n 50
    
    For large files, avoid loading entire file into memory.
    """
    with path.open('r', encoding='utf-8') as f:
        # Skip to start_line
        for _ in range(start_line - 1):
            next(f, None)
        
        # Read line_count lines (or rest of file)
        lines = []
        for i, line in enumerate(f):
            if line_count and i >= line_count:
                break
            lines.append(line)
        
        return ''.join(lines)
```

#### 3. Safe File Writing

```python
def _write_file_safe(
    path: Path,
    content: str,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Safe file write with temp file + atomic rename.
    
    Inspired by: sed -i implementation (GNU sed source)
    
    Algorithm:
    1. Write to temp file in same directory
    2. Preserve original permissions (if file exists)
    3. Atomic rename (temp → original)
    4. Cleanup temp on error
    """
    import tempfile
    import shutil
    
    # Create parent directories if needed
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temp file first (same directory = same filesystem = atomic rename)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp"
    )
    
    try:
        # Write content
        with open(temp_fd, 'w', encoding=encoding) as f:
            f.write(content)
        
        # Preserve permissions if file exists
        if path.exists():
            shutil.copystat(path, temp_path)
        
        # Atomic rename (POSIX guarantees atomicity)
        os.replace(temp_path, path)
        
        return {
            "success": True,
            "action": "write",
            "path": str(path),
            "message": f"Wrote {len(content)} bytes to {path.name}",
            "size_bytes": len(content.encode(encoding)),
            "lines": content.count('\n') + 1
        }
        
    except Exception as e:
        # Cleanup temp file on error
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise
```

### Example Scenarios

#### Scenario 1: Database Specialist Writes Analysis

```python
# Sub-agent writes comprehensive analysis
result = await pos_filesystem(
    action="write",
    path="workspace/analysis/database-schema-analysis.md",
    content="""
# Database Schema Analysis

## Current State
...

## Proposed Changes
...

## Migration Strategy
...
"""
)

# Returns:
{
    "success": True,
    "action": "write",
    "path": "workspace/analysis/database-schema-analysis.md",
    "message": "Wrote 1,234 bytes to database-schema-analysis.md",
    "size_bytes": 1234,
    "lines": 42
}
```

#### Scenario 2: Security Specialist Reads Config

```python
# Sub-agent reads partial config file (large file)
result = await pos_filesystem(
    action="read",
    path="config/settings.py",
    start_line=100,
    line_count=50
)

# Returns:
{
    "success": True,
    "action": "read",
    "path": "config/settings.py",
    "message": "Read lines 100-150 from settings.py",
    "content": "# Configuration lines 100-150...",
    "lines": 50,
    "size_bytes": 1500
}
```

#### Scenario 3: API Specialist Checks File Existence

```python
# Sub-agent checks if API spec exists before generating
result = await pos_filesystem(
    action="exists",
    path="docs/api-spec.yaml"
)

# Returns:
{
    "success": True,
    "action": "exists",
    "path": "docs/api-spec.yaml",
    "message": "File exists: docs/api-spec.yaml",
    "exists": True
}
```

#### Scenario 4: Testing Specialist Creates Directory Structure

```python
# Sub-agent creates test directory
result = await pos_filesystem(
    action="mkdir",
    path="tests/integration/api"
)

# Returns:
{
    "success": True,
    "action": "mkdir",
    "path": "tests/integration/api",
    "message": "Created directory: tests/integration/api"
}
```

---

## Options Considered

### Option A: Granular Tools (Industry Standard)

**Approach:** Separate MCP tool for each operation (following Cline, LangChain, Cursor, Claude Code pattern)

```python
# 6 separate MCP tools
read_file(path, start_line?, line_count?)
write_file(path, content)
list_directory(path)
delete_file(path)
file_exists(path)
make_directory(path)
```

**Pros:**
- ✅ Industry standard pattern (all 5 agent frameworks use this)
- ✅ Clear, single-purpose tools
- ✅ Easy to understand (one tool = one operation)
- ✅ Follows MCP best practices (granular over parameterized)
- ✅ Simpler testing (each tool independently testable)

**Cons:**
- ❌ 6 tools added to sub-agent tool budget (vs. 1 tool)
- ❌ Total tools: 11 (search_standards, pos_workflow, pos_browser, + 6 file tools)
- ❌ Approaching 20-tool threshold where performance degrades (Microsoft research)
- ❌ Inconsistent with prAxIs OS pattern (pos_workflow, pos_browser use actions)
- ❌ More tools = more discovery overhead for sub-agents

**Trade-offs:**
- Gain: Simplicity, industry alignment
- Lose: Tool count budget, pattern consistency

---

### Option B: Consolidated Tool with Action Dispatch (Agent OS Pattern)

**Approach:** Single `pos_filesystem` tool with action parameter (following pos_workflow, pos_browser pattern)

```python
# 1 consolidated MCP tool
pos_filesystem(
    action: Literal["read", "write", "list", "delete", "exists", "mkdir"],
    path: str,
    **kwargs
)
```

**Pros:**
- ✅ Consistent with prAxIs OS pattern (pos_workflow, pos_browser)
- ✅ Low tool count (1 tool vs. 6 tools)
- ✅ Total tools: 6 (well under 20-tool threshold)
- ✅ Domain-first thinking (filesystem = one domain)
- ✅ Room for growth (can add actions without new tools)
- ✅ Discovery via search_standards (patterns documented)

**Cons:**
- ❌ Against industry standard (no other agent uses this pattern)
- ❌ More complex tool signature (multiple actions, conditional params)
- ❌ Requires action parameter understanding
- ❌ Against MCP best practices (consolidation over granular)

**Trade-offs:**
- Gain: Tool count efficiency, pattern consistency, scalability
- Lose: Industry alignment, per-tool simplicity

---

### Option C: Hybrid - Minimal Primitives Only

**Approach:** Provide only read/write, teach composition for everything else

```python
# 2 MCP tools
read_file(path, start_line?, line_count?)
write_file(path, content, create_dirs=True)

# Standards teach composition:
# - Append: read + concatenate + write
# - Delete: (main agent only, too dangerous)
# - List: (main agent only, use glob/search_standards)
# - Exists: try read, handle error
```

**Pros:**
- ✅ Absolute minimal tool count (2 tools)
- ✅ Pure Unix philosophy (compose from primitives)
- ✅ Forces sub-agents to think in primitives
- ✅ Read + write are truly atomic operations

**Cons:**
- ❌ More work for sub-agents (must compose manually)
- ❌ Error-prone (forget to read before write = overwrite)
- ❌ Missing essential operations (list, exists, mkdir)
- ❌ Sub-optimal (no atomic delete, no directory operations)

**Trade-offs:**
- Gain: Extreme minimalism
- Lose: Usability, essential operations

---

### Recommendation: Option B (Consolidated Tool)

**Rationale:**

1. **Consistent with prAxIs OS Architecture**
   - `pos_workflow` uses action dispatch successfully
   - `pos_browser` uses action dispatch successfully
   - `pos_filesystem` continues the pattern

2. **Tool Count Budget is Critical**
   - Sub-agents have tool budget constraints
   - 6 tools (Option A) vs. 1 tool (Option B) = 5-tool savings
   - Enables future capabilities without hitting 20-tool limit

3. **Discovery Pattern Proven**
   - prAxIs OS teaches `search_standards("how to use pos_filesystem")`
   - Dynamic discovery via IDE autocomplete
   - Standards document patterns (append = read + write)

4. **Implementation is Still Granular**
   - Each action → focused function (Unix philosophy preserved)
   - Testing granular (test _read_file, _write_file independently)
   - Code organization clean (operations/ directory)

5. **Agent OS is Different**
   - Industry standard optimizes for cold-start, one-shot tasks
   - prAxIs OS optimizes for long sessions with discovery training
   - Different constraints = different optimal solution

**The consolidation IS the innovation.** Industry pattern is correct for their constraints. prAxIs OS pattern is correct for ours.

---

## Risks & Mitigations

### Risk 1: Security - Path Traversal

**Risk:** Sub-agent escapes workspace via `../../` or symlinks
**Probability:** Medium (if not validated properly)
**Impact:** Critical (access to system files, credentials)

**Mitigation:**
- Strict path validation on all operations
- Resolve symlinks and check final path
- Test with adversarial inputs (`../../etc/passwd`, `/etc/passwd`, etc.)

**Contingency:**
- Add .aosignore support (like .clineignore)
- Audit log all file operations
- Consider read-only mode for sensitive sub-agents

---

### Risk 2: Performance - Large File Reads

**Risk:** Sub-agent reads 1GB log file, causes OOM
**Probability:** Medium (sub-agents might not know file sizes)
**Impact:** High (MCP server crash, all sub-agents affected)

**Mitigation:**
- Default max_size_mb limit (10MB)
- Enforce partial reads for large files
- Return error if file > max_size

**Contingency:**
- Stream reading for very large files
- Provide `file_size` action to check before reading
- Document partial read patterns in standards

---

### Risk 3: Complexity - Action Dispatch Learning Curve

**Risk:** Sub-agents struggle with action-based dispatch
**Probability:** Low (Agent OS teaches discovery)
**Impact:** Medium (sub-agents don't use tool effectively)

**Mitigation:**
- Comprehensive standards documentation
- Examples for every action
- Clear error messages guide correct usage
- IDE autocomplete shows all actions + params

**Contingency:**
- Monitor sub-agent usage patterns
- Refine standards if confusion observed
- Consider granular tools in v2 if needed

---

### Risk 4: Portability - Platform Differences

**Risk:** Implementation works on Unix but breaks on Windows
**Probability:** Low (pure Python is portable)
**Impact:** High (Windows users blocked)

**Mitigation:**
- Use pathlib (cross-platform path handling)
- Use os.replace() (atomic on all platforms)
- Test on Windows, macOS, Linux
- Avoid shell commands

**Contingency:**
- Platform-specific implementations if needed
- Document platform limitations
- Provide fallback implementations

---

### Risk 5: Atomicity - Race Conditions

**Risk:** Two sub-agents write same file simultaneously
**Probability:** Low (PersonaLauncher likely runs sub-agents sequentially)
**Impact:** Medium (file corruption, lost data)

**Mitigation:**
- Use atomic operations (os.replace for writes)
- Temp file + rename (atomic on POSIX)
- File locking if needed

**Contingency:**
- Add file locking support
- Document sequential execution requirement
- Consider transaction log

---

## Open Questions

### Question 1: Should we include "append" action?

**Context:** All frameworks compose append (read + concatenate + write). Should we provide it as built-in action?

**Options:**
- **A:** Include `append` action (convenience)
- **B:** Teach composition via standards (purity)

**Recommendation:** B (teach composition)
- Keeps action count minimal (6 not 7)
- Teaches composability
- Easy to add later if usage shows need

**Decision Needed:** Human approval on composition vs. convenience trade-off

---

### Question 2: Should we include "edit" (search/replace) action?

**Context:** All frameworks (Cline, Cursor, Claude Code) have dedicated edit tools. This is different cognitive model than write.

**Options:**
- **A:** Include `edit` action with old_string/new_string
- **B:** Teach composition (read + replace + write)

**Recommendation:** B (teach composition for MVP)
- Can add in v2 if usage shows it's essential
- Keeps MVP simple
- Sub-agents mostly write new files, not edit existing

**Decision Needed:** Is targeted editing important enough for MVP?

---

### Question 3: What about binary files?

**Context:** Specs, analysis docs, code files are text (UTF-8). But what about images, PDFs generated by sub-agents?

**Options:**
- **A:** Support binary mode (`encoding="binary"`)
- **B:** Text only in MVP, defer binary to future tools (pos_image, pos_pdf)

**Recommendation:** B (text only MVP)
- Sub-agents primarily produce text deliverables
- Binary support adds complexity
- Future: specialized tools for binary formats

**Decision Needed:** Are there critical binary file use cases?

---

### Question 4: Should we expose to main agent or sub-agents only?

**Context:** Main agent (Cursor) has its own file tools. Should main agent also use pos_filesystem?

**Options:**
- **A:** Sub-agents only (PersonaLauncher tool registry)
- **B:** Both main and sub-agents (universal tool)

**Recommendation:** A (sub-agents only for MVP)
- Main agent has Cursor's file tools
- Avoid confusion (two ways to do same thing)
- Can expose to main agent later if beneficial

**Decision Needed:** Is there value in main agent using pos_filesystem?

---

## Success Criteria

### Quantitative Metrics

1. **Tool Count** - Total sub-agent tools ≤ 10 (currently 5 + 1 pos_filesystem = 6 ✅)
2. **Coverage** - 100% of essential file operations (read, write, list, delete, exists, mkdir)
3. **Performance** - File operations complete in <100ms for files <1MB
4. **Safety** - 0 path traversal vulnerabilities (validated by security test suite)
5. **Cross-platform** - Works on Windows, macOS, Linux (100% test pass rate on all platforms)

### Qualitative Outcomes

1. **Sub-agent autonomy** - Database specialist can complete analysis without main agent intervention
2. **Deliverable creation** - Specialists write comprehensive analysis docs (>1000 lines)
3. **Discovery ease** - Sub-agents discover file operations via IDE autocomplete + standards
4. **Error clarity** - File operation errors guide sub-agents to correct usage
5. **Pattern learning** - Sub-agents learn compositions (append = read + write)

### Acceptance Criteria

- [ ] Sub-agent can write analysis document to `workspace/analysis/`
- [ ] Sub-agent can read existing project files with partial read support
- [ ] Sub-agent can check file existence before operations
- [ ] Sub-agent can create directory structures for deliverables
- [ ] Sub-agent cannot escape workspace (path traversal tests pass)
- [ ] Sub-agent gets clear error messages on failures
- [ ] Operations work identically on Windows/macOS/Linux
- [ ] Tool appears in IDE autocomplete with full schema
- [ ] Standards document usage patterns (append, copy, etc.)
- [ ] All operations return structured JSON (not text)

---

## File Change Summary

### Files to Create

**MCP Tool Registration:**
- `mcp_server/tools/pos_filesystem/__init__.py` - Tool registration
- `mcp_server/tools/pos_filesystem/dispatcher.py` - Action routing

**Implementation Layer:**
- `mcp_server/tools/pos_filesystem/operations/read.py` - Read implementation
- `mcp_server/tools/pos_filesystem/operations/write.py` - Write implementation
- `mcp_server/tools/pos_filesystem/operations/list.py` - List implementation
- `mcp_server/tools/pos_filesystem/operations/delete.py` - Delete implementation
- `mcp_server/tools/pos_filesystem/operations/exists.py` - Exists implementation
- `mcp_server/tools/pos_filesystem/operations/mkdir.py` - Mkdir implementation

**Safety Layer:**
- `mcp_server/tools/pos_filesystem/safety/validation.py` - Path validation
- `mcp_server/tools/pos_filesystem/safety/sandboxing.py` - Workspace scoping

**Tests:**
- `mcp_server/tools/pos_filesystem/tests/test_read.py`
- `mcp_server/tools/pos_filesystem/tests/test_write.py`
- `mcp_server/tools/pos_filesystem/tests/test_list.py`
- `mcp_server/tools/pos_filesystem/tests/test_delete.py`
- `mcp_server/tools/pos_filesystem/tests/test_exists.py`
- `mcp_server/tools/pos_filesystem/tests/test_mkdir.py`
- `mcp_server/tools/pos_filesystem/tests/test_security.py` - Path traversal tests
- `mcp_server/tools/pos_filesystem/tests/test_integration.py` - End-to-end tests

**Documentation:**
- `.praxis-os/standards/development/aos-filesystem-usage.md` - Usage patterns
- `.praxis-os/standards/development/aos-filesystem-patterns.md` - Composition patterns

### Files to Modify

- `mcp_server/server.py` - Register pos_filesystem tool
- `mcp_server/core/persona_launcher.py` - Add pos_filesystem to sub-agent tool registry
- `.praxis-os/standards/development/mcp-tool-design-best-practices.md` - Document pos_ pattern

### Dependencies Impacted

- None (uses Python stdlib: pathlib, os, tempfile, shutil)

---

## Testing Approach

### Unit Tests

**Test each operation independently:**

```python
# test_read.py
def test_read_full_file()
def test_read_partial_file()
def test_read_nonexistent_file()
def test_read_file_too_large()
def test_read_binary_file_error()

# test_write.py
def test_write_new_file()
def test_write_overwrite_file()
def test_write_creates_parent_dirs()
def test_write_atomic_operation()
def test_write_preserves_permissions()

# test_security.py (CRITICAL)
def test_path_traversal_blocked()
def test_absolute_path_blocked()
def test_symlink_escape_blocked()
def test_hidden_file_access()
```

### Integration Tests

**Test full MCP call flow:**

```python
# test_integration.py
async def test_sub_agent_writes_analysis():
    """Test database specialist writes analysis doc."""
    result = await pos_filesystem(
        action="write",
        path="workspace/analysis/test-doc.md",
        content="# Test\n\nContent"
    )
    assert result["success"] == True
    assert Path("workspace/analysis/test-doc.md").exists()

async def test_composition_pattern():
    """Test append composition (read + write)."""
    # Write initial content
    await pos_filesystem(action="write", path="log.txt", content="Line 1\n")
    
    # Append by reading + concatenating + writing
    read_result = await pos_filesystem(action="read", path="log.txt")
    new_content = read_result["content"] + "Line 2\n"
    await pos_filesystem(action="write", path="log.txt", content=new_content)
    
    # Verify
    final = await pos_filesystem(action="read", path="log.txt")
    assert "Line 1\nLine 2\n" in final["content"]
```

### Cross-Platform Tests

```python
# Run on Windows, macOS, Linux
@pytest.mark.parametrize("platform", ["windows", "macos", "linux"])
def test_atomic_write_cross_platform(platform):
    """Verify atomic writes work on all platforms."""
    # Test os.replace() atomicity
    # Test pathlib compatibility
    # Test encoding handling
```

### Security Tests

```python
def test_adversarial_paths():
    """Test malicious path inputs."""
    bad_paths = [
        "../../etc/passwd",
        "/etc/passwd",
        "../.ssh/id_rsa",
        "workspace/../../etc/passwd",
        "workspace/../../../root/.bash_history"
    ]
    
    for bad_path in bad_paths:
        with pytest.raises(ValueError, match="Path traversal"):
            validate_path(bad_path, project_root)
```

### Validation Methods

1. **Automated tests** - pytest suite runs on PR, commit
2. **Manual testing** - Test with actual PersonaLauncher + database specialist
3. **Security audit** - Adversarial testing with path traversal attempts
4. **Performance testing** - Large file handling (10MB, 100MB limits)
5. **Platform testing** - CI/CD on Windows, macOS, Linux

---

## Prior Art & Standing on Shoulders of Giants

### Unix Tools (Source Code Study)

**sed (GNU sed source):**
- Safe in-place editing: temp file + atomic rename
- Algorithm: read → write temp → rename temp → original
- We adopt: `_write_file_safe()` uses same approach

**tail (coreutils source):**
- Efficient last-N-lines: seek to end, scan backwards for newlines
- Avoids reading entire file into memory
- We adopt: `_read_file_partial()` for efficient line ranges

**grep (GNU grep source):**
- Binary file detection: check for NUL bytes in first 8KB
- Context lines: ring buffer for -B, lookahead for -A
- We defer: No search in MVP, but learned detection patterns

### Agent Frameworks (Real-World Implementations)

**Cline (6 file tools):**
- Separate read/write/edit/list/search/delete
- Granular pattern, auto-approval flow
- We learned: Industry uses granular for good reason (safety, clarity)

**Cursor (6 file tools):**
- Partial read (offset + limit) - ESSENTIAL for large files
- Search/replace separate from write
- We adopt: Partial read support in `read` action

**Claude Code (6 file tools):**
- Workflow rules: "Read before edit/write"
- Special format handling (images, PDFs, notebooks)
- We learned: Read-before-write as best practice (document in standards)

**LangChain (7 file tools):**
- Granular: read, write, list, delete, copy, move, search
- Append as parameter to write (not separate tool)
- We consider: Append as composition (teach pattern)

**CrewAI (2 file tools):**
- Minimal: read (with line ranges!), write
- Partial read: start_line, line_count parameters
- We adopt: Line range parameters for partial reads

### BuilderMethods Agent OS

**Philosophical Foundation:**
- 3-layer structure (workflows, standards, usage)
- Documentation as runtime (RAG/MCP)
- We build on: Infrastructure to scale the vision

---

## Appendices

### A. Research Data

All research repositories cloned to `/tmp/pos_filesystem_research/`:
- `cline/` - Cline file handlers
- `langchain-community/` - LangChain file management tools
- `AutoGPT/` - AutoGPT file manager
- `crewAI/` - CrewAI file tools
- `sweep/` - Sweep file operations

Full analysis: `workspace/analysis/aos-filesystem-research-findings.md`

### B. Unix Source References

**GNU sed:**
- Repository: https://git.savannah.gnu.org/cgit/sed.git
- Key files: `sed/execute.c`, `sed/compile.c`, `sed/utils.c`

**GNU grep:**
- Repository: https://git.savannah.gnu.org/cgit/grep.git
- Key files: `src/grep.c`, `src/kwset.c`, `src/dfa.c`

**coreutils:**
- Repository: https://github.com/coreutils/coreutils
- Key files: `src/head.c`, `src/tail.c`, `src/cp.c`, `src/rm.c`

### C. Related Standards

- `search_standards("mcp tool design")` - MCP best practices
- `search_standards("unix philosophy")` - Do one thing well
- `search_standards("workspace organization")` - Where files go
- `search_standards("sub-agent tools")` - PersonaLauncher tool registry

---

## Decision Required

**Human Review Needed:**

1. ✅ **Approve Option B** (consolidated tool) vs. Option A (granular tools)?
2. ✅ **Approve 6 actions** (read, write, list, delete, exists, mkdir) as MVP?
3. ✅ **Defer append/edit** to post-MVP (teach composition)?
4. ✅ **Text files only** in MVP (defer binary to specialized tools)?
5. ✅ **Sub-agents only** (don't expose to main agent)?

**Next Steps After Approval:**

1. Create spec via `spec_creation_v1` workflow
2. Use this design doc as input to inform SRD, specs.md, tasks.md
3. Execute spec via `spec_execution_v1` workflow
4. Test with real sub-agents (database specialist, security specialist)

---

**End of Design Document**

**Status**: Ready for Human Review  
**Next**: Approval → `spec_creation_v1` → `spec_execution_v1` → Implementation

