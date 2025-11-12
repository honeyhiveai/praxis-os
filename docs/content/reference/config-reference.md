---
sidebar_position: 2
doc_type: reference
---

# Configuration Reference

Complete reference for `.praxis-os/config/mcp.yaml` configuration file.

## Overview

The `mcp.yaml` file configures what prAxIs OS indexes and how it searches your project. It's located at `.praxis-os/config/mcp.yaml` and is created during installation.

**⚠️ Critical:** After installation, you **must** customize the code indexing paths (`code.source_paths` and `ast.source_paths`) to match your project's structure.

**Path Resolution:**
- All paths are relative to `.praxis-os/` directory (not project root)
- Example: If your code is at `project-root/src/`, use `"../src/"`
- Example: If your code is at `project-root/lib/`, use `"../lib/"`

---

## Configuration Structure

```yaml
version: "1.0"

indexes:
  standards: { ... }
  code: { ... }
  ast: { ... }
  file_watcher: { ... }

workflow: { ... }
browser: { ... }
logging: { ... }
```

---

## Indexes Configuration

### Standards Index

Indexes documentation and markdown files for semantic search.

**Default:** Usually fine as-is unless you have custom documentation locations.

```yaml
standards:
  source_paths:
    - "standards/"  # Relative to .praxis-os/
  
  vector:
    model: "BAAI/bge-small-en-v1.5"  # Embedding model
    dimension: 384  # Model dimension (384 for small, 768 for base, 1024 for large)
    chunk_size: 800  # Tokens per chunk (~2-3 paragraphs)
    chunk_overlap: 100  # Overlap between chunks (~1-2 sentences)
  
  fts: {}  # Full-text search defaults
  
  metadata_filtering:
    enabled: true
    scalar_indexes:
      - column: "domain"
        index_type: "BTREE"
      - column: "phase"
        index_type: "BITMAP"
      - column: "section"
        index_type: "BTREE"
    auto_generate: true  # Extract metadata from headers
    llm_enhance: false  # Optional LLM-based metadata enhancement
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `source_paths` | list[string] | `["standards/"]` | Directories to index (relative to `.praxis-os/`) |
| `vector.model` | string | `"BAAI/bge-small-en-v1.5"` | Embedding model (see Embedding Models section below) |
| `vector.dimension` | integer | `384` | Model dimension (must match model) |
| `vector.chunk_size` | integer | `800` | Tokens per chunk (larger = more context) |
| `vector.chunk_overlap` | integer | `100` | Overlap between chunks |
| `metadata_filtering.enabled` | boolean | `true` | Enable metadata pre-filtering |
| `metadata_filtering.auto_generate` | boolean | `true` | Auto-extract metadata from headers |
| `metadata_filtering.llm_enhance` | boolean | `false` | Use LLM for better metadata (costs money) |

**Embedding Models:**

| Model | Size | Dimensions | Speed | Accuracy | Use Case |
|-------|------|------------|-------|----------|----------|
| `BAAI/bge-small-en-v1.5` | 134MB | 384 | Fast | Good | **Default** - Best balance |
| `BAAI/bge-base-en-v1.5` | 438MB | 768 | Medium | Better | Larger projects |
| `BAAI/bge-large-en-v1.5` | 1.3GB | 1024 | Slow | Best | Maximum accuracy needed |

All models are MIT licensed, zero cost, and run offline.

---

### Code Index

**⚠️ CRITICAL: Must customize for your project!**

Indexes source code for semantic search and call graph traversal.

```yaml
code:
  source_paths:
    - "../src/"  # ⚠️ CHANGE THIS: Your project's source paths
  
  languages:
    - "python"  # ⚠️ UPDATE THIS: Languages your project uses
  
  vector:
    model: "microsoft/codebert-base"  # Code-specific embedding model
    dimension: 768  # CodeBERT uses 768 dimensions
    chunk_size: 200  # Smaller chunks = function-level precision
    chunk_overlap: 20  # Prevents function splitting
  
  fts: {}  # Full-text search defaults
  
  graph: {}  # Call graph defaults (max_depth=10)
  
  duckdb_path: ".cache/code.duckdb"  # Call graph database location
  
  respect_gitignore: true  # ✅ Automatically respect .gitignore patterns (recommended)
  exclude_patterns: []  # Optional: Additional exclusion patterns (gitignore format)
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `source_paths` | list[string] | `["ouroboros/"]` | **⚠️ REQUIRED:** Your source code directories |
| `languages` | list[string] | `["python"]` | **⚠️ REQUIRED:** Languages to index |
| `vector.model` | string | `"microsoft/codebert-base"` | Code embedding model |
| `vector.dimension` | integer | `768` | Model dimension (768 for CodeBERT) |
| `vector.chunk_size` | integer | `200` | Tokens per chunk (smaller = more precision) |
| `vector.chunk_overlap` | integer | `20` | Overlap between chunks |
| `duckdb_path` | string | `".cache/code.duckdb"` | Call graph database location |
| `respect_gitignore` | boolean | `true` | **✅ NEW:** Automatically respect `.gitignore` patterns (recommended) |
| `exclude_patterns` | list[string] | `null` | **✅ NEW:** Additional exclusion patterns in gitignore format (merged with `.gitignore`) |

**File Exclusion System:**

prAxIs OS uses a **three-tier exclusion system** to automatically skip unwanted files. All pattern matching uses proper gitignore syntax via the `gitignore-parser` library (required dependency).

1. **Tier 1: `.gitignore` patterns** (if `respect_gitignore: true`)
   - Automatically reads and respects your project's `.gitignore` file
   - Zero-config for most projects
   - Works exactly like `git status` - files ignored by git are excluded from indexing
   - Uses proper gitignore pattern matching (not simple substring matching)

2. **Tier 2: Built-in defaults** (when no `.gitignore` exists or `respect_gitignore: false`)
   - Comprehensive patterns covering 200+ common build artifacts
   - Python: `__pycache__/`, `.tox/`, `.pytest_cache/`, `dist/`, `build/`, etc.
   - JavaScript: `node_modules/`, `.next/`, `dist/`, `build/`, etc.
   - Rust: `target/`, Go: `vendor/`, Java: `.gradle/`, etc.
   - IDEs, OS files, logs, databases, secrets, etc.
   - Uses proper gitignore pattern matching (same as Tier 1)

3. **Tier 3: Config `exclude_patterns`** (additive override)
   - Additional patterns you specify in config
   - Merged with `.gitignore` (both apply)
   - Use gitignore format: `"custom_build/", "*.generated.py"`
   - Uses proper gitignore pattern matching (same as Tier 1)

**Example with Custom Exclusions:**

```yaml
code:
  source_paths:
    - "../src/"  # ✅ Can now use top-level directory!
  
  respect_gitignore: true  # Default - respects .gitignore automatically
  exclude_patterns:  # Additional patterns beyond .gitignore
    - "custom_build_dir/**"
    - "*.generated.py"
    - "test_fixtures/"
  
  languages: ["python"]
```

**Benefits:**
- ✅ **Zero-config:** Most projects work out-of-the-box with `.gitignore`
- ✅ **No crashes:** Build artifacts automatically excluded
- ✅ **Clean search:** Only source code indexed, not dependencies
- ✅ **Flexible:** Add custom patterns when needed
- ✅ **Proper pattern matching:** Uses `gitignore-parser` library for accurate gitignore-compatible pattern matching (required dependency)

**Common Project Patterns:**

**Python:**
```yaml
source_paths:
  - "../src/"
  - "../lib/"
languages:
  - "python"
```

**JavaScript/TypeScript:**
```yaml
source_paths:
  - "../src/"
  - "../app/"
  - "../components/"
languages:
  - "javascript"
  - "typescript"
```

**Next.js:**
```yaml
source_paths:
  - "../app/"
  - "../components/"
  - "../lib/"
languages:
  - "typescript"
```

**Go:**
```yaml
source_paths:
  - "../cmd/"
  - "../pkg/"
  - "../internal/"
languages:
  - "go"
```

**Rust:**
```yaml
source_paths:
  - "../src/"
languages:
  - "rust"
```

**Monorepo:**
```yaml
source_paths:
  - "../packages/*/src/"
  - "../apps/*/src/"
languages:
  - "typescript"
  - "python"
```

**Multi-language:**
```yaml
source_paths:
  - "../src/python/"
  - "../src/typescript/"
  - "../src/go/"
languages:
  - "python"
  - "typescript"
  - "go"
```

**Supported Languages:**
- `python`
- `javascript`
- `typescript`
- `go`
- `rust`

---

### Multi-Repo Code Intelligence 🚀

**NEW:** Index and search across multiple local repositories simultaneously!

prAxIs OS now supports multi-repo code intelligence, allowing you to search and analyze code across multiple related repositories (framework + SDK, monorepo services, multi-language projects, etc.).

#### Configuration Modes

**Single-Repo Mode (Legacy):**
```yaml
code:
  source_paths: ["../src/"]
  languages: ["python"]
```

**Multi-Repo Mode (NEW):**
```yaml
code:
  partitions:
    praxis-os:
      path: .  # Relative to .praxis-os/
      domains:
        code:
          include_paths: [ouroboros/, scripts/]
        tests:
          include_paths: [tests/]
    
    python-sdk:
      path: ../../python-sdk  # Sibling repository
      domains:
        code:
          include_paths: [src/]
          metadata:
            project: python-sdk
            type: library
```

#### Multi-Repo Concepts

**What is a Partition?**
- A partition is an isolated code index for a single repository
- Each partition has its own semantic index and call graph
- Partitions can be searched individually or together
- Changes in one partition don't affect others

**What are Domains?**
- Domains are logical groupings within a partition (code, tests, docs)
- Each domain can have different `include_paths` and metadata
- Allows fine-grained control over what gets indexed

**Directory Layout:**
```
.praxis-os/
├── .cache/indexes/code/
│   ├── praxis-os/         # Partition 1
│   │   ├── semantic/      # LanceDB vector index
│   │   └── graph.duckdb   # DuckDB call graph
│   └── python-sdk/        # Partition 2
│       ├── semantic/      # LanceDB vector index
│       └── graph.duckdb   # DuckDB call graph
```

#### Multi-Repo Examples

**Example 1: Framework + SDK**
```yaml
code:
  partitions:
    praxis-os:
      path: .
      domains:
        code:
          include_paths: [ouroboros/]
        tests:
          include_paths: [tests/]
    
    python-sdk:
      path: ../../python-sdk
      domains:
        code:
          include_paths: [src/]
        tests:
          include_paths: [tests/]
```

**Use Case:** Search across framework implementation and SDK client code simultaneously

**Example 2: Monorepo with Multiple Services**
```yaml
code:
  partitions:
    api-service:
      path: ../services/api
      domains:
        code:
          include_paths: [src/]
    
    worker-service:
      path: ../services/worker
      domains:
        code:
          include_paths: [src/]
    
    shared-lib:
      path: ../packages/shared
      domains:
        code:
          include_paths: [lib/]
```

**Use Case:** Analyze interactions between microservices and shared libraries

**Example 3: Multi-Language Project**
```yaml
code:
  partitions:
    backend:
      path: ../backend
      domains:
        code:
          include_paths: [src/]
      metadata:
        language: python
    
    frontend:
      path: ../frontend
      domains:
        code:
          include_paths: [src/, components/]
      metadata:
        language: typescript
```

**Use Case:** Understand full-stack architecture across language boundaries

#### Multi-Repo Search Patterns

**Search all repositories:**
```python
pos_search_project(
    action="search_code",
    query="authentication logic",
    n_results=10
)
```

**Search specific repository:**
```python
pos_search_project(
    action="search_code",
    query="tracer implementation",
    filters={"partition": "python-sdk"},
    n_results=5
)
```

**Graph traversal (requires partition filter):**
```python
# ⚠️ CRITICAL: Call graph actions MUST specify partition
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    filters={"partition": "python-sdk"},
    max_depth=5
)
```

#### Multi-Repo Configuration Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `partitions` | dict | Yes | Dictionary of partition configs (key = partition name) |
| `partitions.<name>.path` | string | Yes | Repository path relative to `.praxis-os/` |
| `partitions.<name>.domains` | dict | Yes | Domain configs (code, tests, docs, etc.) |
| `partitions.<name>.domains.<domain>.include_paths` | list[string] | Yes | Paths to index within the repository |
| `partitions.<name>.domains.<domain>.exclude_patterns` | list[string] | No | Additional gitignore patterns |
| `partitions.<name>.domains.<domain>.metadata` | dict | No | Custom metadata tags |

#### Critical Notes

1. **Path Resolution:** All paths are relative to `.praxis-os/` directory
   - Current repo: `path: .`
   - Parent directory: `path: ..`
   - Sibling repo: `path: ../../other-repo`

2. **Call Graph Requirement:** Graph traversal actions (`find_callers`, `find_dependencies`, `find_call_paths`) **require** a partition filter in multi-repo mode because call graphs are partition-specific.

3. **Declarative Reconciliation:** When you modify the config, the system automatically:
   - Creates new partition indexes on startup
   - Deletes removed partition indexes
   - No manual commands needed - just edit config and restart

4. **Use `include_paths` for selective indexing:** Instead of indexing entire repositories, specify exact directories (e.g., `[src/]`) to avoid indexing virtual environments, build artifacts, etc.

#### Migration from Single-Repo to Multi-Repo

**Before (Single-Repo):**
```yaml
code:
  source_paths: ["../src/"]
  languages: ["python"]
```

**After (Multi-Repo):**
```yaml
code:
  partitions:
    my-project:
      path: ..
      domains:
        code:
          include_paths: [src/]
  languages: ["python"]  # Still needed at top level
```

#### Multi-Repo Benefits

- ✅ **Cross-Repo Search:** Find similar code patterns across all repositories
- ✅ **SDK Integration Analysis:** Understand how SDKs integrate with frameworks
- ✅ **Bug Tracing:** Trace issues that span multiple repositories
- ✅ **Architecture Comparison:** Compare implementation patterns between projects
- ✅ **Zero Maintenance:** Declarative config auto-reconciles on startup

---

### AST Index

**⚠️ CRITICAL: Must customize for your project!**

Indexes code structure using Tree-sitter AST parsing.

```yaml
ast:
  source_paths:
    - "../src/"  # ⚠️ Should match code.source_paths
  
  languages:
    - "python"  # ⚠️ Should match code.languages
  
  auto_install_parsers: true  # Auto-install missing parsers
  venv_path: "venv/"  # Isolated venv for parsers
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `source_paths` | list[string] | `["ouroboros/"]` | **⚠️ REQUIRED:** Should match `code.source_paths` |
| `languages` | list[string] | `["python"]` | **⚠️ REQUIRED:** Should match `code.languages` |
| `auto_install_parsers` | boolean | `true` | Auto-install missing Tree-sitter parsers |
| `venv_path` | string | `"venv/"` | Isolated venv for parser installation |

**Note:** If `auto_install_parsers: false`, you must manually install parsers for air-gapped environments.

---

### File Watcher

Automatically rebuilds indexes when files change.

```yaml
file_watcher:
  enabled: true  # Enable automatic rebuilds
  debounce_ms: 500  # Wait 500ms after last change before rebuilding
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable automatic index rebuilding |
| `debounce_ms` | integer | `500` | Milliseconds to wait after last change |

**Disable if:** You want manual rebuilds only (use `IndexManager.rebuild_index()` programmatically).

---

## Workflow Configuration

Configures phase-gated workflow execution.

```yaml
workflow:
  workflows_dir: "workflows/"  # Workflow definitions location
  state_dir: ".cache/state/"  # Workflow state persistence
  session_timeout_minutes: 1440  # 24 hours
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `workflows_dir` | string | `"workflows/"` | Directory containing workflow definitions |
| `state_dir` | string | `".cache/state/"` | Directory for workflow state files |
| `session_timeout_minutes` | integer | `1440` | Session timeout (24 hours) |

---

## Browser Configuration

Configures browser automation (Playwright).

```yaml
browser:
  browser_type: "chromium"  # Options: chromium, firefox, webkit
  headless: true  # Run without UI
  max_sessions: 10  # Max concurrent sessions
  session_timeout_minutes: 30  # Auto-cleanup idle sessions
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `browser_type` | string | `"chromium"` | Browser engine (`chromium`, `firefox`, `webkit`) |
| `headless` | boolean | `true` | Run without UI (set `false` for debugging) |
| `max_sessions` | integer | `10` | Maximum concurrent browser sessions |
| `session_timeout_minutes` | integer | `30` | Auto-cleanup idle sessions after timeout |

---

## Logging Configuration

Configures structured logging and behavioral metrics.

```yaml
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "text"  # Options: "text" or "json"
  log_dir: ".cache/logs/"  # Log file location
  behavioral_metrics_enabled: true  # Track query diversity, trends
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | `"INFO"` | Log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `format` | string | `"text"` | Log format (`"text"` for human-readable, `"json"` for structured) |
| `log_dir` | string | `".cache/logs/"` | Directory for log files |
| `behavioral_metrics_enabled` | boolean | `true` | Track query diversity, trends, prepend effectiveness |

---

## Configuration Examples

### Minimal Python Project

```yaml
version: "1.0"

indexes:
  standards:
    source_paths: ["standards/"]
  
  code:
    source_paths: ["../src/"]
    languages: ["python"]
  
  ast:
    source_paths: ["../src/"]
    languages: ["python"]
  
  file_watcher: {}

workflow: {}
browser: {}
logging: {}
```

### TypeScript/Next.js Project

```yaml
version: "1.0"

indexes:
  standards:
    source_paths: ["standards/"]
  
  code:
    source_paths:
      - "../app/"
      - "../components/"
      - "../lib/"
    languages:
      - "typescript"
      - "javascript"
  
  ast:
    source_paths:
      - "../app/"
      - "../components/"
      - "../lib/"
    languages:
      - "typescript"
      - "javascript"
  
  file_watcher: {}

workflow: {}
browser: {}
logging: {}
```

### Monorepo (Multiple Packages)

```yaml
version: "1.0"

indexes:
  standards:
    source_paths: ["standards/"]
  
  code:
    source_paths:
      - "../packages/*/src/"
      - "../apps/*/src/"
    languages:
      - "typescript"
      - "python"
  
  ast:
    source_paths:
      - "../packages/*/src/"
      - "../apps/*/src/"
    languages:
      - "typescript"
      - "python"
  
  file_watcher: {}

workflow: {}
browser: {}
logging: {}
```

### High-Performance Configuration

```yaml
version: "1.0"

indexes:
  standards:
    source_paths: ["standards/"]
    vector:
      model: "BAAI/bge-base-en-v1.5"  # Better accuracy
      dimension: 768
      chunk_size: 1000  # Larger chunks
  
  code:
    source_paths: ["../src/"]
    languages: ["python"]
    vector:
      model: "microsoft/codebert-base"
      dimension: 768
      chunk_size: 300  # Larger chunks for more context
  
  ast:
    source_paths: ["../src/"]
    languages: ["python"]
  
  file_watcher:
    enabled: true
    debounce_ms: 1000  # Longer debounce for large projects

workflow:
  session_timeout_minutes: 2880  # 48 hours

browser:
  max_sessions: 20  # More concurrent sessions

logging:
  level: "DEBUG"
  format: "json"  # Structured logging
```

### Multi-Repo Configuration (Framework + SDK)

```yaml
version: "1.0"

indexes:
  standards:
    source_paths: ["standards/"]
  
  code:
    partitions:
      praxis-os:
        path: .
        domains:
          code:
            include_paths: [ouroboros/, scripts/]
          tests:
            include_paths: [tests/]
            metadata:
              type: tests
      
      python-sdk:
        path: ../../python-sdk
        domains:
          code:
            include_paths: [src/]
            metadata:
              project: python-sdk
              type: library
          tests:
            include_paths: [tests/]
            metadata:
              project: python-sdk
              type: tests
    
    languages: ["python"]
    vector:
      model: "microsoft/codebert-base"
      dimension: 768
  
  ast:
    source_paths: ["../src/"]  # Not used in multi-repo mode
    languages: ["python"]
  
  file_watcher:
    enabled: true

workflow: {}
browser: {}
logging: {}
```

---

## Troubleshooting

### "No results from code search"

**Cause:** Code paths not configured correctly or all files excluded.

**Fix:**
1. Check `code.source_paths` in `mcp.yaml`
2. Verify paths are relative to `.praxis-os/` directory
3. Ensure paths exist (use `../src/` not `src/`)
4. Check if files are being excluded:
   - Verify `.gitignore` isn't excluding your source files
   - Check `exclude_patterns` in config
   - Temporarily set `respect_gitignore: false` to test
5. Rebuild index: Restart MCP server (auto-builds) or use `IndexManager.rebuild_index()`

### "Files being excluded that shouldn't be"

**Cause:** Exclusion patterns too aggressive.

**Fix:**
1. Check your `.gitignore` file - it's automatically respected (uses proper gitignore pattern matching)
2. Use negation patterns in `.gitignore`: `!important_file.py`
3. Or disable gitignore: `respect_gitignore: false` (uses built-in defaults only, still with proper pattern matching)
4. Or add negation to `exclude_patterns`: `["!important_file.py"]`

**Note:** Pattern matching uses the `gitignore-parser` library (required dependency) for accurate gitignore-compatible behavior. All patterns follow standard gitignore syntax rules.

### "Index not found" errors

**Cause:** Indexes haven't been built yet.

**Fix:**
1. Wait 10-30 seconds for file watcher to build indexes
2. Or restart MCP server (auto-builds missing indexes)
3. Check `.praxis-os/.cache/indexes/` directory exists

### "Parser not found" for AST search

**Cause:** Tree-sitter parser not installed.

**Fix:**
1. Set `ast.auto_install_parsers: true` (requires internet)
2. Restart MCP server (it will auto-install)
3. Or manually install: `pip install tree-sitter-python` (for Python)

### "Path traversal detected" errors

**Cause:** Invalid path configuration.

**Fix:**
1. Use relative paths only (e.g., `../src/` not `/absolute/path`)
2. Don't use `..` outside project root
3. Ensure paths are relative to `.praxis-os/` directory

### Slow search performance

**Cause:** Large indexes or inefficient configuration.

**Fix:**
1. Reduce `chunk_size` for faster indexing
2. Enable `metadata_filtering` (already enabled by default)
3. Use smaller embedding model (`bge-small` instead of `bge-large`)
4. Increase `file_watcher.debounce_ms` to reduce rebuild frequency

---

## Related Documentation

- [Installation Guide](../tutorials/installation.md) - Initial setup and customization
- [MCP Tools Reference](./mcp-tools.md) - Available search tools

