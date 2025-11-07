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

**Disable if:** You want manual rebuilds only (use `build_rag_index.py` script).

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

---

## Troubleshooting

### "No results from code search"

**Cause:** Code paths not configured correctly.

**Fix:**
1. Check `code.source_paths` in `mcp.yaml`
2. Verify paths are relative to `.praxis-os/` directory
3. Ensure paths exist (use `../src/` not `src/`)
4. Rebuild index: `python .praxis-os/scripts/build_rag_index.py`

### "Index not found" errors

**Cause:** Indexes haven't been built yet.

**Fix:**
1. Wait 10-30 seconds for file watcher to build indexes
2. Or manually rebuild: `python .praxis-os/scripts/build_rag_index.py`
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

