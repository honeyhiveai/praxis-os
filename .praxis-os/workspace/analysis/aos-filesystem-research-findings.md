# aos_filesystem Research Findings

**Research Date:** 2025-10-25  
**Purpose:** Analyze real-world agent file operation patterns to inform `aos_filesystem` tool design

---

## Summary of Findings

Analyzed 5 major open-source agent frameworks to understand file operation patterns, API design, and safety mechanisms.

### Repositories Analyzed

1. **Cline** (VS Code extension) - TypeScript
2. **LangChain** (agent framework) - Python
3. **AutoGPT** (autonomous agent) - Python
4. **CrewAI** (multi-agent framework) - Python
5. **Sweep** (AI code reviewer) - Python

---

## 1. Cline File Operations

### Tools Provided (6 file-related tools)

```typescript
enum ClineDefaultTool {
    FILE_READ = "read_file",           // Read file contents
    FILE_NEW = "write_to_file",        // Create/overwrite file
    FILE_EDIT = "replace_in_file",     // Edit existing file with diff
    LIST_FILES = "list_files",         // List directory contents
    SEARCH = "search_files",           // Search files with regex
    LIST_CODE_DEF = "list_code_definition_names"  // List code symbols
}
```

### Key Design Patterns

**1. Separate Tools (NOT Consolidated)**
- Each operation is a distinct tool
- No action-based dispatch
- Total: 6 file-related tools

**2. ReadFile Tool**
```typescript
Parameters:
  - path: string (required)

Features:
  - Workspace-scoped paths
  - Multi-workspace support with hints
  - Handles images (if model supports)
  - Approval flow (auto-approve or manual)
  - Telemetry tracking
  - .clineignore support (security)

Returns: File content as text
```

**3. WriteToFile Tool (Handles both write_to_file and replace_in_file)**
```typescript
Parameters:
  - path: string (required)
  - content: string (for write_to_file)
  - diff: string (for replace_in_file)

Features:
  - Creates file if doesn't exist
  - Opens diff view for edits
  - Streams content in real-time (partial blocks)
  - User can edit before approval
  - Auto-formatting detection
  - Linter integration (shows problems)
  - Distinguishes "create" vs "modify"
  - Security: .clineignore paths blocked

Returns: Success message with diagnostics
```

**4. ListFiles Tool**
```typescript
Parameters:
  - path: string (required)
  - recursive: boolean (optional)

Features:
  - Top-level or recursive listing
  - Limit: 200 files (prevents overwhelming output)
  - .clineignore filtering

Returns: Formatted file list
```

**5. SearchFiles Tool**
```typescript
Parameters:
  - regex: string (required)
  - file_pattern: string (optional)
  - path: string (optional)

Features:
  - Regex search via ripgrep
  - File pattern filtering (glob)
  - Multi-workspace support
  - Result count reporting
  - .clineignore filtering

Returns: Search results with line numbers
```

### Safety Mechanisms

1. **Workspace Scoping** - All paths relative to workspace root
2. **.clineignore** - Block access to sensitive paths
3. **Approval Flow** - User must approve destructive operations
4. **Path Validation** - Prevents directory traversal
5. **Multi-root Workspace** - Workspace hints for disambiguation

---

## 2. LangChain File Operations

### Tools Provided (7 separate tools)

```python
# LangChain provides GRANULAR tools, not consolidated

1. ReadFileTool
2. WriteFileTool
3. ListDirectoryTool
4. DeleteFileTool
5. CopyFileTool
6. MoveFileTool
7. FileSearchTool
```

### Key Design Patterns

**1. Granular Tools (MCP Best Practice Pattern)**
- Each operation is a separate tool
- Simple, focused responsibility
- No action dispatch

**2. ReadFileTool**
```python
Parameters:
  - file_path: str

Features:
  - Path validation via BaseFileToolMixin
  - UTF-8 encoding
  - Error handling (file not found, permission denied)

Returns: File content as string
```

**3. WriteFileTool**
```python
Parameters:
  - file_path: str
  - text: str
  - append: bool = False

Features:
  - Write or append mode
  - Creates parent directories automatically
  - UTF-8 encoding
  - Path validation

Returns: Success message
```

**4. ListDirectoryTool**
```python
Parameters:
  - dir_path: str = "."

Features:
  - Lists files and directories
  - Simple output (one per line)

Returns: Newline-separated list
```

**5. DeleteFileTool**
```python
Parameters:
  - file_path: str

Features:
  - Path validation
  - Existence check
  - os.remove() for deletion

Returns: Success message
```

**6. CopyFileTool**
```python
Parameters:
  - source_path: str
  - destination_path: str

Features:
  - Uses shutil.copy2 (preserves metadata)
  - Path validation for both source and dest
  - follow_symlinks=False

Returns: Success message
```

**7. MoveFileTool**
```python
Parameters:
  - source_path: str
  - destination_path: str

Features:
  - Uses shutil.move
  - Path validation

Returns: Success message
```

### Safety Mechanisms

1. **BaseFileToolMixin** - Shared path validation logic
2. **get_relative_path()** - Sandboxes to root directory
3. **Error handling** - All exceptions caught and returned as strings

---

## 3. AutoGPT File Operations

### Tools Provided (3 core operations)

```python
# AutoGPT FileManagerComponent provides:

1. read_file
2. write_to_file (aliases: write_file, create_file)
3. list_folder
```

### Key Design Patterns

**1. Minimal Set**
- Only essential operations
- No copy/move/delete exposed to agent
- Focus on read/write/list

**2. Workspace Separation**
```python
self.storage       # Agent-related files (state, logs)
self.workspace     # Agent's working files
```

**3. ReadFile**
```python
Parameters:
  - filename: str | Path

Features:
  - Binary read + decode
  - Handles multiple text encodings
  - Workspace-scoped

Returns: Decoded text content
```

**4. WriteToFile**
```python
Parameters:
  - filename: str
  - contents: str

Features:
  - Overwrites if exists
  - Workspace-scoped

Returns: Success message with path
```

**5. ListFolder**
```python
Parameters:
  - folder: str

Features:
  - Workspace-scoped
  - Simple listing

Returns: List of entries
```

### Safety Mechanisms

1. **Workspace Sandboxing** - Separate storage vs workspace
2. **FileStorage Abstraction** - Can use local, S3, or GCS
3. **Limited Operations** - No delete/move exposed

---

## 4. CrewAI File Operations

### Tools Provided (2 tools)

```python
1. FileReadTool
2. FileWriterTool
```

### Key Design Patterns

**1. Minimal Tools**
- Only read and write
- No list/delete/copy/move

**2. FileReadTool**
```python
Parameters:
  - file_path: str
  - start_line: int | None = 1
  - line_count: int | None = None

Features:
  - Partial file reading (line ranges!)
  - Optional default file_path at construction
  - Error handling (not found, permission, generic)

Returns: File content (full or partial)
```

**3. FileWriterTool**
```python
Parameters:
  - filename: str
  - content: str
  - directory: str | None = "./"
  - overwrite: str | bool = False

Features:
  - Creates directory if needed
  - Overwrite protection
  - Separate filename and directory

Returns: Success message with full path
```

### Notable Features

1. **Partial File Reading** - start_line and line_count for large files
2. **Overwrite Protection** - Explicit flag required
3. **Directory Creation** - Automatic parent directory creation

---

## 5. Tool Count Comparison

| Framework | File Tools | Pattern | Notes |
|-----------|------------|---------|-------|
| Cline | 6 | Separate Tools | read, write, edit, list, search, list_code_def |
| LangChain | 7 | Separate Tools | read, write, list, delete, copy, move, search |
| AutoGPT | 3 | Separate Tools | read, write, list |
| CrewAI | 2 | Separate Tools | read, write |
| Sweep | ? | (Not fully analyzed) | |

**Key Insight:** ALL frameworks use SEPARATE TOOLS, not action-based consolidation!

---

## 6. Common Patterns Across All Frameworks

### Operations Provided

| Operation | Cline | LangChain | AutoGPT | CrewAI |
|-----------|-------|-----------|---------|--------|
| Read | ✅ | ✅ | ✅ | ✅ |
| Write | ✅ | ✅ | ✅ | ✅ |
| Append | ❌ (use edit) | ✅ (param) | ❌ | ❌ |
| List Dir | ✅ | ✅ | ✅ | ❌ |
| Delete | ❌ | ✅ | ❌ | ❌ |
| Copy | ❌ | ✅ | ❌ | ❌ |
| Move | ❌ | ✅ | ❌ | ❌ |
| Search | ✅ | ✅ | ❌ | ❌ |
| Edit (diff) | ✅ | ❌ | ❌ | ❌ |
| Partial Read | ❌ | ❌ | ❌ | ✅ |

### Safety Patterns

1. **Workspace Scoping** (All)
   - All paths relative to workspace root
   - Prevents directory traversal

2. **Path Validation** (All)
   - Validation before any file operation
   - Return errors as strings (don't raise)

3. **Approval Flows** (Cline only)
   - User must approve destructive operations
   - Auto-approval for trusted paths

4. **Ignore Files** (Cline only)
   - .clineignore blocks sensitive paths

5. **Error Handling** (All)
   - All exceptions caught
   - Returned as error strings (not raised)

### Return Value Patterns

1. **Success Messages** - Human-readable confirmation
2. **File Content** - For read operations
3. **Error Strings** - "Error: <description>"
4. **Path Confirmation** - Echo the path in response

---

## 7. Design Insights for aos_filesystem

### Insight 1: Granular vs. Consolidated

**Finding:** ALL frameworks use separate tools, NOT action-based consolidation.

**But:** This conflicts with Agent OS's `aos_` pattern (workflow, browser use actions)

**Resolution Options:**

**Option A: Follow Industry Pattern (Granular)**
```python
# Separate MCP tools (7 tools)
read_file(path)
write_file(path, content)
append_file(path, content)
list_directory(path)
delete_file(path)
copy_file(source, dest)
move_file(source, dest)
```

**Option B: Agent OS Pattern (Consolidated)**
```python
# Single tool with actions (1 tool)
aos_filesystem(
    action: "read" | "write" | "append" | "list" | "delete" | "copy" | "move",
    path: str,
    content: Optional[str],
    destination: Optional[str]
)
```

**Recommendation:** Option B (consolidated) because:
- ✅ Consistent with `aos_workflow` and `aos_browser`
- ✅ Keeps tool count low (6 total vs 13+)
- ✅ Agent OS teaches dynamic discovery (overcomes consolidation complexity)
- ✅ Microsoft research applies to generic agents (not Agent OS trained agents)

### Insight 2: Essential Operations

**Minimum Viable Set (Based on usage across all frameworks):**

1. **read** - Read file contents (all frameworks)
2. **write** - Create or overwrite file (all frameworks)
3. **append** - Append to existing file (LangChain, useful for logs)
4. **list** - List directory contents (most frameworks)
5. **delete** - Delete file (LangChain, useful for cleanup)
6. **exists** - Check if file/dir exists (implied in all)
7. **mkdir** - Create directory (implied in write operations)

**Optional (Advanced):**
- copy - Copy file (LangChain only)
- move - Move file (LangChain only)
- search - Search file contents (Cline, LangChain)

**Recommendation:** Start with essential 7, add advanced later if needed.

### Insight 3: Safety is Critical

**Required Safety Mechanisms:**

1. **Workspace Scoping** - All paths relative to project root
2. **Path Validation** - Prevent directory traversal (`../../etc/passwd`)
3. **Error Handling** - Return errors as strings, never raise
4. **Size Limits** - Cap file size for read operations (prevent memory issues)
5. **Encoding** - Default to UTF-8, handle binary files

**Optional (Future):**
- Approval flow (like Cline)
- .aosignore file (like .clineignore)
- Telemetry tracking

### Insight 4: Return Value Format

**Consistent Return Format:**

```python
{
    "success": bool,
    "action": str,
    "path": str,
    "message": str,
    "content": Optional[str],  # For read operations
    "error": Optional[str]      # If success=false
}
```

### Insight 5: Unique Features to Consider

**From CrewAI:**
- Partial file reading (start_line, line_count) - EXCELLENT for large files!

**From Cline:**
- Recursive listing with limits - Prevents overwhelming output
- Search integration - Already have RAG, but file search is different
- Edit with diff - Advanced, defer for now

**From LangChain:**
- Append as parameter - Simpler than separate action
- Automatic directory creation - Essential for write operations

### Insight 6: Sub-Agent Specific Needs

**Specialists will primarily:**

1. **Write output** - Analysis docs, specs, code files
2. **Read input** - Existing code, config files
3. **Append to logs** - Progress tracking
4. **List directories** - Explore project structure
5. **Create directories** - Organize output

**Less likely to:**
- Delete files (main agent's job)
- Copy/move files (main agent's job)
- Search files (use search_standards or grep via main agent)

**Recommendation:** Focus on write, read, append, list, mkdir for MVP.

---

## 8. Recommended aos_filesystem Design

### Tool Signature

```python
@mcp.tool()
async def aos_filesystem(
    action: Literal["read", "write", "append", "list", "delete", "exists", "mkdir"],
    path: str,
    content: Optional[str] = None,
    encoding: str = "utf-8",
    start_line: Optional[int] = None,  # For partial read (from CrewAI)
    line_count: Optional[int] = None,  # For partial read (from CrewAI)
    create_dirs: bool = True,          # Auto-create parent dirs (from LangChain)
    max_size_mb: int = 10              # Safety limit for read
) -> Dict[str, Any]:
    """
    File system operations for Agent OS sub-agents.
    
    Provides OS-level file I/O capabilities to autonomous agents.
    All paths are workspace-scoped for security.
    
    Actions:
        read: Read file contents (supports partial read with line ranges)
        write: Write/overwrite file (creates parent dirs if needed)
        append: Append to existing file
        list: List directory contents (non-recursive)
        delete: Delete file or empty directory
        exists: Check if path exists
        mkdir: Create directory
    
    Args:
        action: Operation to perform
        path: File/directory path relative to project root
        content: Content to write/append (for write/append actions)
        encoding: File encoding (default: utf-8)
        start_line: Start reading from this line (1-indexed, for read)
        line_count: Number of lines to read (None = all, for read)
        create_dirs: Auto-create parent directories (for write/append)
        max_size_mb: Max file size to read in MB (safety limit)
    
    Returns:
        {
            "success": bool,
            "action": str,
            "path": str,
            "message": str,
            "content": Optional[str],  # For read
            "exists": Optional[bool],  # For exists
            "entries": Optional[List[str]],  # For list
            "error": Optional[str]
        }
    
    Examples:
        # Write analysis document
        await aos_filesystem(
            action="write",
            path="workspace/analysis/database-schema.md",
            content="# Database Schema\\n\\n..."
        )
        
        # Read file (partial)
        result = await aos_filesystem(
            action="read",
            path="src/models/user.py",
            start_line=50,
            line_count=20
        )
        
        # Append to log
        await aos_filesystem(
            action="append",
            path="workspace/specialist-log.md",
            content="\\n## Database Review Complete\\n"
        )
        
        # List directory
        result = await aos_filesystem(action="list", path="src/")
        
        # Check existence
        result = await aos_filesystem(action="exists", path="config/settings.json")
    """
```

### Safety Implementation

```python
class FileSystemSafety:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
    
    def validate_path(self, path: str) -> Path:
        """Validate and resolve path within workspace."""
        # Remove leading slash, resolve relative to project root
        clean_path = path.lstrip("/")
        resolved = (self.project_root / clean_path).resolve()
        
        # Ensure path is within project root
        if not str(resolved).startswith(str(self.project_root)):
            raise ValueError(
                f"Path traversal detected: {path} resolves outside project root"
            )
        
        return resolved
    
    def check_file_size(self, path: Path, max_size_mb: int) -> None:
        """Check file size before reading."""
        if path.exists() and path.is_file():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise ValueError(
                    f"File too large: {size_mb:.1f}MB exceeds limit of {max_size_mb}MB"
                )
```

---

## 9. Next Steps

1. **Create Detailed Spec** - Full design document for `aos_filesystem`
2. **Review with User** - Confirm consolidated vs granular decision
3. **Implement MVP** - Start with essential operations (read, write, append, list, mkdir)
4. **Test with Sub-Agents** - Validate in persona system
5. **Iterate** - Add advanced operations (delete, copy, move, search) if needed

---

## 10. Key Decisions to Confirm with User

### Decision 1: Consolidated vs. Granular

**Question:** Use single `aos_filesystem(action, ...)` or separate tools (`read_file`, `write_file`, etc.)?

**Industry Pattern:** All frameworks use granular (separate tools)

**Agent OS Pattern:** Consolidated (`aos_workflow`, `aos_browser`)

**Recommendation:** Consolidated (consistent with Agent OS, lower tool count)

### Decision 2: Operation Set

**Question:** What operations to include in MVP?

**Recommendation:**
- MVP: read, write, append, list, exists, mkdir (6 actions)
- Future: delete, copy, move, search

### Decision 3: Partial Read Feature

**Question:** Include start_line/line_count for partial reads? (from CrewAI)

**Recommendation:** YES - Essential for large files, minimal complexity

### Decision 4: Return Format

**Question:** Consistent dict format vs. action-specific returns?

**Recommendation:** Consistent dict with optional fields

---

## Appendix: Research File Locations

All research repos located in: `/tmp/aos_filesystem_research/`

- `cline/` - Cline file handlers
- `langchain-community/` - LangChain file management tools
- `AutoGPT/` - AutoGPT file manager component
- `crewAI/` - CrewAI file tools
- `sweep/` - Sweep file operations

---

**End of Research Findings**

