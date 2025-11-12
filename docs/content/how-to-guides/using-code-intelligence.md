---
sidebar_position: 8
doc_type: how-to
---

# Using Code Intelligence Effectively

This guide covers practical patterns for using prAxIs OS code intelligence: when to use semantic search vs AST vs graph traversal, how to construct effective queries, and how to set up multi-repo indexing.

**You'll learn:**
- Quick start (single-repo in 2 minutes)
- When to use which search type
- How to write effective queries
- Multi-repo setup (framework + SDK)
- Cross-repo discovery patterns
- Troubleshooting common issues

---

## Quick Start: Single Repository

**Fastest path from zero to searching code:**

### Step 1: Configure Paths (2 minutes)

Edit `.praxis-os/config/mcp.yaml`:

```yaml
indexes:
  code:
    source_paths:
      - "../src/"  # ⚠️ CHANGE THIS to your source directory
    languages:
      - "python"   # ⚠️ CHANGE THIS to your language(s)
  
  ast:
    source_paths:
      - "../src/"  # Should match code.source_paths
    languages:
      - "python"   # Should match code.languages
```

**Path resolution:** Relative to `.praxis-os/` directory
- Your code at `project-root/src/` → use `"../src/"`
- Your code at `project-root/lib/` → use `"../lib/"`

### Step 2: Restart MCP Server

Indexes build automatically on first start (~2-4 seconds for 1,000 files).

### Step 3: Search Your Code

```python
# Ask a question in natural language
pos_search_project(
    action="search_code",
    query="How does authentication work?",
    n_results=5
)
```

**Done!** You're now searching code by meaning, not exact text.

---

## When to Use Which Search Type

### Semantic Search (`search_code`)

**Use when:**
- Exploring unfamiliar codebase
- Don't know exact function names
- Want conceptually similar code
- Cross-language search needed

**Examples:**
- Query `"authentication and authorization logic"` finds auth code regardless of whether it's named `authenticate`, `login`, or `verify_token`
- Query `"error handling with retries and exponential backoff"` returns retry patterns across your codebase
- Query `"input validation and sanitization"` works across Python, JavaScript, Go, etc.

**Query patterns that work well:**
- "How does X work?" → Returns implementation chunks
- "Where is Y handled?" → Returns relevant code sections
- "[concept] implementation" → Returns code matching concept

### AST Search (`search_ast`)

**Use when:**
- Need exact syntax patterns
- Language-specific queries
- Structure matters more than meaning

**Examples:**
- Query `"async def"` finds all async functions in Python
- Query `"try:"` finds all exception handlers
- Query `"class"` finds all class definitions

**Pattern syntax:** Tree-sitter patterns (language-specific)
- Python: `async def`, `class`, `try:`, `with`, `@decorator`
- JavaScript: `async function`, `class`, `try`, `=>`, `import`
- Go: `func`, `type`, `interface`, `defer`

### Graph Traversal (`find_callers`, `find_dependencies`, `find_call_paths`)

**Use when:**
- Need to understand control flow
- Impact analysis ("What breaks if I change this?")
- Find dead code ("Nothing calls this")
- Trace execution paths

**Examples:**
- `find_callers` on `process_payment` shows who calls this function (up to 5 levels deep)
- `find_dependencies` on `validate_user` shows what this function calls
- `find_call_paths` from `start_workflow` to `validate_phase` shows the execution path

**Symbol names:** Use exact function/method names
- Python: `ClassName.method_name` or `function_name`
- JavaScript: `ClassName.methodName` or `functionName`
- Go: `FunctionName` (exported) or `functionName` (internal)

---

## Writing Effective Queries

### Semantic Search Query Patterns

**✅ Good queries (descriptive, specific):**
- `"authentication middleware that validates JWT tokens"` - Describes what you're looking for
- `"database connection pooling with retry logic"` - Uses domain concepts
- `"CSV file parsing with error handling"` - Specific functionality

**❌ Poor queries (vague, too generic):**
- `"auth"` - Too vague, returns everything
- `"function"` - Single word (use AST search instead)
- `"What is AuthService? How does it work? Where is it called?"` - Multiple unrelated concepts

**Pro tips:**
- Use 5-10 words for best results
- Include domain terms ("JWT", "CSV", "webhook")
- Describe *what* the code does, not variable names
- Ask complete questions, not fragments

### AST Search Pattern Syntax

**✅ Exact matches work best:**

**Python:** `"async def"` (all async functions), `"class"` (all classes), `"@dataclass"` (all dataclasses), `"try:"` (all try blocks)

**JavaScript/TypeScript:** `"async function"`, `"class"`, `"=> {"` (arrow functions), `"import"`

**Note:** AST search is syntax-aware, not semantic. Query `"authentication"` won't find auth-related code unless the word appears in function names/comments.

### Graph Traversal Query Patterns

**Symbol naming conventions:**
- **Python:** `ClassName.method_name`, `ClassName.__init__`, `module.function_name`, or `function_name`
- **JavaScript/TypeScript:** `ClassName.methodName`, `ClassName.constructor`, or `functionName`
- **Go:** `PackageName.FunctionName`, `TypeName.MethodName`

**Max depth guidelines:**
- `max_depth=3` → Direct callers/dependencies only
- `max_depth=5` → Typical use case (2-3 hops)
- `max_depth=10` → Deep traversal (may be slow)
- `max_depth=20` → Entire call tree (use sparingly)

---

## Multi-Repo Setup

### Use Case: Framework + SDK

**Scenario:** You maintain a framework (praxis-os) and an SDK (python-sdk). You want to:
- Search both repositories simultaneously
- Understand how SDK integrates with framework
- Find similar patterns across both codebases

### Step 1: Configure Multi-Repo

Edit `.praxis-os/config/mcp.yaml`:

```yaml
indexes:
  code:
    partitions:
      praxis-os:
        path: .  # Current repo (.praxis-os/)
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
          tests:
            include_paths: [tests/]
            metadata:
              project: python-sdk
              type: tests
    
    languages: ["python"]  # Still needed at top level
```

**Path resolution:**
```
/Users/you/projects/
├── praxis-os/
│   └── .praxis-os/       ← config here
└── python-sdk/           ← ../../python-sdk from .praxis-os/
```

### Step 2: Use `include_paths` for Selective Indexing

**Why:** Repositories often have build artifacts, virtual environments, node_modules, etc.

**Example:**

```yaml
python-sdk:
  path: ../../python-sdk
  domains:
    code:
      include_paths: [src/]  # ✅ Only index src/ directory
```

**Without `include_paths`:** Would index entire repo including `venv/`, `dist/`, `.tox/` → slow, wrong results

**With `include_paths`:** Indexes only `src/` → fast, accurate

### Step 3: Restart MCP Server

```bash
# System reconciles partitions automatically
# Creates: .praxis-os/.cache/indexes/code/python-sdk/
```

**Declarative reconciliation:** Edit config → restart → done. No manual commands needed.

### Step 4: Search Across Repos

```python
# Search ALL repositories (default)
pos_search_project(
    action="search_code",
    query="How does the tracer send events?",
    n_results=10
)
# Returns results from BOTH praxis-os and python-sdk

# Search specific repository
pos_search_project(
    action="search_code",
    query="HoneyHiveTracer implementation details",
    filters={"partition": "python-sdk"},
    n_results=5
)
# Returns results ONLY from python-sdk
```

**Graph traversal requires partition:**

```python
# ⚠️ MUST specify partition for call graphs
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    filters={"partition": "python-sdk"},  # Required
    max_depth=5
)
```

**Why?** Call graphs are partition-specific (can't resolve imports across repos).

---

## Multi-Repo Discovery Patterns

### Pattern 1: Find Similar Implementations

**Use case:** "Does the SDK implement the same pattern as the framework?"

1. Query `"retry logic with exponential backoff"` with `filters={"partition": "praxis-os"}` 
2. Query same with `filters={"partition": "python-sdk"}`
3. Compare implementations manually

### Pattern 2: Understand SDK Integration

**Use case:** "How does the SDK use the framework's API?"

1. Query `"workflow execution and phase validation"` in python-sdk partition
2. Use `find_dependencies` on `sdk_client.start_workflow` to trace calls
3. Review how SDK integrates with framework

### Pattern 3: Cross-Repo Bug Tracing

**Use case:** "Bug might be in framework OR SDK, not sure which."

Query `"null pointer exception handling in async code"` without partition filter → returns ranked results from **both** repos. Partition metadata shows which repo each result is from.

### Pattern 4: Architecture Comparison

**Use case:** "How does error handling differ between framework and SDK?"

1. Query `"error handling and exception strategies"` in praxis-os partition
2. Query same in python-sdk partition
3. Compare: Do both use `ActionableError`? Do retry strategies match?

---

## Understanding Search Results

### Semantic Search Results

**Result structure:**

```python
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "def authenticate(token: str) -> User:\n    ...",
      "file": "src/auth/middleware.py",
      "start_line": 45,
      "end_line": 58,
      "relevance_score": 0.89,
      "partition": "praxis-os",  # Which repo
      "domain": "code",           # vs tests/docs
      "metadata": {}
    }
  ]
}
```

**Key fields:**
- `relevance_score`: 0.0-1.0 (higher = more relevant)
- `partition`: Which repository (multi-repo mode)
- `file` + `start_line`/`end_line`: Exact location

**Interpreting scores:**
- 0.85-1.0: Highly relevant
- 0.70-0.85: Probably relevant
- Below 0.70: May not be what you want

### AST Search Results

**Result structure:**

```python
{
  "status": "success",
  "action": "search_ast",
  "results": [
    {
      "node_type": "function_definition",
      "name": "authenticate",
      "file": "src/auth/middleware.py",
      "start_line": 45,
      "end_line": 58,
      "text": "async def authenticate(token: str) -> User:\n    ...",
      "partition": "praxis-os"
    }
  ]
}
```

**Key fields:**
- `node_type`: AST node type (`function_definition`, `class_definition`, etc.)
- `name`: Symbol name
- `text`: Full node source code

### Graph Traversal Results

**Result structure (callers):**

```python
{
  "status": "success",
  "action": "find_callers",
  "results": [
    {
      "symbol": "HoneyHiveTracer.__init__",
      "depth": 0,
      "callers": [
        {
          "symbol": "HoneyHive.init_tracer",
          "file": "src/client.py",
          "line": 234,
          "depth": 1
        },
        {
          "symbol": "HoneyHive.__init__",
          "file": "src/client.py",
          "line": 67,
          "depth": 2
        }
      ]
    }
  ]
}
```

**Key fields:**
- `depth`: Call chain depth (0 = target, 1 = direct caller, 2 = caller's caller)
- `symbol`: Function/method name
- Hierarchical structure shows call chain

---

## Common Workflows

### Workflow 1: Explore Unfamiliar Codebase

**Goal:** Understand authentication system

1. **Semantic search** for `"authentication system overview"` → Get high-level understanding
2. **AST search** for `"def authenticate"` → Find entry points
3. **Graph traversal** with `find_callers` on `authenticate` → Trace who uses it

### Workflow 2: Impact Analysis

**Goal:** "What breaks if I change this function?"

1. **Graph traversal** with `find_callers` on `validate_user` (deep, `max_depth=10`) → See all callers
2. **Semantic search** for `"tests for validate_user callers"` in tests domain → Check coverage
3. **Semantic search** for `"user validation similar to validate_user"` → Find similar functions that might break too

### Workflow 3: Find and Fix Anti-Pattern

**Goal:** "Find all uses of deprecated API"

1. **AST search** for `"old_api_call"` → Find exact textual uses
2. **Semantic search** for `"old API usage pattern"` → Find conceptual uses (might use different names)
3. **Semantic search** for `"new API recommended usage"` → Find replacement examples

---

## Troubleshooting

### No Results from Search

**Symptom:** Query returns 0 results

**Cause 1: Paths not configured**

Check `mcp.yaml` - paths must be relative to `.praxis-os/`:
- ❌ Wrong: `source_paths: ["src/"]` (relative to project root)
- ✅ Right: `source_paths: ["../src/"]` (relative to `.praxis-os/`)

**Fix:** Update paths in `mcp.yaml`, restart server.

**Cause 2: Files excluded by gitignore**

Check with `git status --ignored` if your source files are being ignored.

**Fix:** Update `.gitignore` to not ignore source files, or set `respect_gitignore: false` in config.

**Cause 3: Index not built**

Check if `.praxis-os/.cache/indexes/code/` directory exists.

**Fix:** Restart MCP server (auto-builds indexes).

### Wrong Results from Semantic Search

**Symptom:** Results not relevant to query

**Cause 1: Query too vague**
- ❌ Bad: `"auth"` (too generic)
- ✅ Better: `"JWT authentication middleware for API requests"` (specific)

**Cause 2: Code comments misleading**

Example: Function named `authenticate` but comments mention "caching" → semantic search might match cache queries.

**Fix:** Use AST search for exact function names: `"def authenticate"`

### Graph Traversal Returns Empty

**Symptom:** `find_callers` returns no results for known function

**Cause 1: Partition not specified (multi-repo mode)**

In multi-repo mode, graph traversal **requires** partition filter: `filters={"partition": "praxis-os"}`

**Cause 2: Dynamic call not tracked**

Graph traversal can't see dynamic calls like `getattr(obj, "authenticate")()`.

**Fix:** Use semantic search: `"dynamic call to authenticate method"`

**Cause 3: Symbol name incorrect**

Check casing - `"Authenticate"` won't match `authenticate`.

**Fix:** Use AST search to find exact name: `"def auth"` (partial match)

### Slow Queries

**Symptom:** Semantic search takes >500ms

**Cause 1: Too many results requested**

Requesting 100 results is slow. Use `n_results=5` for fast queries.

**Cause 2: Large index (10,000+ files)**

**Fix:** Use partition filters: `filters={"partition": "python-sdk"}` searches 1 repo instead of all.

**Cause 3: Many partitions**

Multi-repo with 5+ partitions queries all in parallel, then merges.

**Fix:** Use partition filters to target specific repos.

### Index Out of Date

**Symptom:** Recent code changes not in search results

**Cause:** File watcher didn't trigger rebuild

**Fix:** Restart MCP server (rebuilds all indexes automatically).

---

## Advanced: Custom Metadata Filtering

### Use Case: Tag Code by Team/Feature

**Config:**

```yaml
python-sdk:
  path: ../../python-sdk
  domains:
    core:
      include_paths: [src/core/]
      metadata:
        team: platform
        feature: core
    integrations:
      include_paths: [src/integrations/]
      metadata:
        team: integrations
        feature: external
```

**Query specific team's code:**

```python
pos_search_project(
    action="search_code",
    query="authentication logic",
    filters={
        "partition": "python-sdk",
        "metadata": {"team": "platform"}
    },
    n_results=5
)
```

**Benefits:**
- Isolate search to specific team's code
- Track feature-specific implementations
- Useful for large teams/codebases

---

## Related Documentation

- [Explanation: Code Intelligence Architecture](../explanation/code-intelligence.md) - How the three-tier system works
- [Reference: MCP Tools](../reference/mcp-tools.md) - Complete tool parameters
- [Reference: Configuration](../reference/config-reference.md) - Multi-repo config options
- [Tutorial: Your First Project Standard](../tutorials/your-first-project-standard.md) - Standards complement code intelligence


