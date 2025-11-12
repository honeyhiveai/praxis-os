---
sidebar_position: 5
doc_type: explanation
---

# Code Intelligence: Three-Tier Search Architecture

prAxIs OS provides code intelligence through three complementary search systems: semantic search (meaning), AST search (structure), and graph traversal (relationships). This document explains why each tier exists, how they work together, and the trade-offs involved.

---

## The Problem

### Traditional Code Search Limitations

**grep/ripgrep:**
- Requires exact text matches
- No understanding of code semantics
- Can't answer "What does this do?" or "Who calls this?"
- Example: `grep "auth"` finds `authenticate()`, `author`, and `auth_token` equally

**IDE "Find References":**
- Single-language, single-repository only
- No cross-language understanding
- Requires project to be open
- Can't answer "How does authentication work?"

**Reading entire files:**
- Context overflow (30 files × 500 lines = 15,000 tokens)
- Wastes 90% of attention on irrelevant code
- Slow, expensive, error-prone
- Doesn't scale to multi-repo codebases

### What's Missing

No single tool answers all three core questions:

1. **"What does this code do?"** (semantic meaning)
2. **"Show me the structure"** (syntax patterns)
3. **"Who calls this function?"** (control flow)

prAxIs OS solves this with a **three-tier architecture** where each tier specializes in one question type.

---

## Architecture Overview

### Three Complementary Tiers

**Tier 1: Semantic Search** (LanceDB + CodeBERT)
- **Purpose:** Find code by meaning, not exact text
- **Technology:** Vector embeddings (768-dimensional)
- **Query:** "How does authentication work?"
- **Returns:** Code chunks semantically related to auth

**Tier 2: AST Search** (DuckDB + Tree-sitter)
- **Purpose:** Find code by structural patterns
- **Technology:** Abstract Syntax Tree indexing
- **Query:** "Find all async functions"
- **Returns:** Exact syntax matches

**Tier 3: Graph Traversal** (DuckDB + Recursive CTEs)
- **Purpose:** Understand call relationships
- **Technology:** Symbol-level call graph
- **Query:** "Who calls `authenticate()`?"
- **Returns:** Call chain with depth

**Why three tiers instead of one?**

Each tier optimizes for different query types. No single index can efficiently answer semantic, structural, and relational questions.

---

## Tier 1: Semantic Search

### How It Works

**Indexing Process:**
1. Code chunked at function/class boundaries (200 tokens avg)
2. Each chunk embedded using CodeBERT (trained on 6.4M code samples)
3. Vectors stored in LanceDB (high-performance vector database)
4. Full-text search index created in parallel (hybrid retrieval)

**Query Process:**
1. Query embedded using same CodeBERT model
2. Vector similarity search (cosine distance)
3. Combined with full-text search (Reciprocal Rank Fusion)
4. Results ranked by relevance score

**Example:**

Query: `"How are errors handled in the tracer?"`

```python
pos_search_project(
    action="search_code",
    query="How are errors handled in the tracer?",
    filters={"partition": "python-sdk"},
    n_results=5
)
```

Returns chunks containing:
- `try/except` blocks in tracer methods
- Error callback functions
- Logging statements in error paths
- Comment explaining error strategy

**Performance:**
- Index build: ~2s per 1,000 files
- Query latency: ~50-100ms
- Memory: ~200MB for 10,000 chunks
- Accuracy: 85-90% relevant results in top 5

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| Finds conceptually similar code | Requires rebuild on changes |
| Language-agnostic (works across Python, JS, Go) | 768-dim vectors = 3KB per chunk |
| No exact keyword needed | May miss exact-match edge cases |
| Hybrid search (vector + FTS) | ~50ms query overhead |

---

## Tier 2: AST Search

### How It Works

**Indexing Process:**
1. Code parsed by Tree-sitter (multi-language parser)
2. AST nodes extracted (function_definition, class_definition, etc.)
3. Node metadata stored in DuckDB (type, name, file, line range)
4. Indexed by node type for fast filtering

**Query Process:**
1. Tree-sitter pattern matched against AST nodes
2. SQL query filters by node type/name
3. Results include file path, line range, full node text

**Example:**

Query: `"async def"`

```python
pos_search_project(
    action="search_ast",
    query="async def",
    filters={"partition": "python-sdk"},
    n_results=10
)
```

Returns:
- All `async def` function definitions
- Exact line ranges
- Full function signature
- File paths

**Performance:**
- Parse time: ~100ms per file (cached)
- Query latency: ~10-20ms (SQL index scan)
- Memory: ~50MB for 1,000 files
- Accuracy: 100% (exact structural match)

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| Exact structural matches | Language-specific patterns |
| Fast SQL queries (10-20ms) | Requires Tree-sitter grammar |
| No false positives | Can't find semantic similarity |
| Low memory footprint | Parse time on first index |

---

## Tier 3: Graph Traversal

### How It Works

**Indexing Process:**
1. AST parsed to extract symbols (functions, classes, methods)
2. Call relationships extracted (X calls Y)
3. Import statements tracked
4. Graph stored in DuckDB (symbols table + relationships table)

**Query Process:**
1. Find symbol by name in symbols table
2. Recursive CTE traverses call graph
3. Returns full call chain with depth
4. Supports forward (dependencies) and backward (callers) traversal

**Example:**

Query: `"Who calls HoneyHiveTracer.__init__?"`

```python
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    filters={"partition": "python-sdk"},
    max_depth=5
)
```

Returns:
```
HoneyHiveTracer.__init__ (depth 0)
  ← HoneyHive.init_tracer() (depth 1)
    ← HoneyHive.__init__() (depth 2)
      ← create_honeyhive_client() (depth 3)
```

**Performance:**
- Graph build: ~1s per 1,000 files
- Query latency: ~20-50ms (recursive CTE)
- Memory: ~30MB for 1,000 files
- Accuracy: 95% (misses dynamic calls)

**Limitations:**
- **Dynamic calls not tracked:** `getattr(obj, method_name)()` → unknown
- **Cross-language calls limited:** Python ↔ JS requires explicit config
- **Partition-specific:** Graph doesn't span repositories (by design)

**Trade-offs:**

| Benefit | Limitation |
|---------|------------|
| Understand control flow | Partition-specific (no cross-repo) |
| Fast recursive queries | Misses dynamic/reflection calls |
| Call depth tracking | Can't track runtime behavior |
| Low memory footprint | Requires symbol resolution |

---

## Multi-Repo Architecture

### Partitioning Strategy

**What is a Partition?**
- Isolated index for a single repository
- Own semantic index + own call graph
- Changes in one partition don't affect others
- Enables framework + SDK + app analysis

**Directory Layout:**
```
.praxis-os/.cache/indexes/code/
├── praxis-os/           # Partition 1
│   ├── semantic/        # LanceDB (vectors + FTS)
│   └── graph.duckdb     # DuckDB (AST + call graph)
└── python-sdk/          # Partition 2
    ├── semantic/        # LanceDB (vectors + FTS)
    └── graph.duckdb     # DuckDB (AST + call graph)
```

**Why partition instead of one index?**

1. **Isolation:** Bug in SDK indexing doesn't break framework search
2. **Performance:** Search 1 partition (1,000 files) instead of 3 (3,000 files)
3. **Incremental updates:** Only rebuild changed partition
4. **Cross-repo discovery:** Find similar patterns across repositories

**Semantic search spans partitions:**

```python
# Search ALL repositories
pos_search_project(
    action="search_code",
    query="authentication logic",
    n_results=10
)
# Returns results from praxis-os AND python-sdk, ranked by relevance
```

**Graph traversal is partition-specific:**

```python
# Must specify partition (call graphs don't span repos)
pos_search_project(
    action="find_callers",
    query="HoneyHiveTracer.__init__",
    filters={"partition": "python-sdk"},
    max_depth=5
)
```

**Why no cross-repo call graphs?**

Call graphs require symbol resolution (imports, function names). Across repositories:
- Import paths differ (`from honeyhive.tracer` vs `from ouroboros.subsystems`)
- Symbol namespaces conflict
- Dynamic imports common (Flask blueprints, plugin systems)
- Runtime behavior unknowable at index time

**Solution:** Semantic search finds integration points, graph traversal understands flow within each repo.

### Declarative Reconciliation

**Concept:** Configuration declares desired state, system reconciles on startup.

**Example:**

```yaml
# mcp.yaml
code:
  partitions:
    praxis-os:
      path: .
    python-sdk:
      path: ../../python-sdk
```

**On startup:**
1. System reads config (desired state: 2 partitions)
2. Scans filesystem (actual state: 1 partition exists)
3. Reconciliation: Create `python-sdk` partition
4. Result: Filesystem matches config

**Add new partition:**
```yaml
# Add to config
    typescript-sdk:
      path: ../../typescript-sdk
```

**Restart server → partition automatically created. No manual commands.**

**Remove partition:**
```yaml
# Remove from config (delete python-sdk entry)
```

**Restart server → partition automatically deleted. Indexes ephemeral (can rebuild).**

**Why declarative instead of imperative?**

| Approach | How | Pro | Con |
|----------|-----|-----|-----|
| Imperative | `create_partition("sdk")` | Explicit control | Requires manual commands |
| Declarative | Edit config, restart | Zero-touch | Requires restart |

prAxIs OS uses declarative (Kubernetes/Terraform-style) because:
- Config is source of truth (version controlled)
- No drift (filesystem always matches config)
- Simpler mental model (edit file, restart, done)

---

## Parse-Once-Index-Thrice Optimization

### The Problem

Each index tier needs parsed AST:
- Semantic index: Extract function/class boundaries for chunking
- AST index: Store node types, names, ranges
- Graph index: Extract symbols and call relationships

**Naive approach:** Parse file 3 times (3× Tree-sitter overhead)

### The Solution

**Parse cache coordinator (`IncrementalIndexer`):**

```python
# Parse file ONCE
ast = tree_sitter.parse(file_content)

# Use same AST for all three indexes
semantic_index.add_chunks(chunk_by_ast(ast))
ast_index.add_nodes(extract_nodes(ast))
graph_index.add_symbols(extract_calls(ast))
```

**On file change:**
1. File watcher detects modification
2. `IncrementalIndexer` parses file once
3. Parsed AST flows to all three indexes
4. Each index performs incremental update

**Performance:**

| Approach | Parse Time (1,000 files) | Memory |
|----------|--------------------------|--------|
| Naive (3× parse) | ~300ms × 3 = 900ms | 150MB × 3 = 450MB |
| Parse-once | ~300ms × 1 = 300ms | 150MB (shared) |
| **Savings** | **67% faster** | **67% less memory** |

**Trade-off:** Complexity (cache invalidation, coordinated updates) for performance.

---

## When to Use Which Tier

### Decision Guide

**Use Semantic Search when:**
- Exploring unfamiliar codebase ("How does X work?")
- Finding conceptually similar code
- Cross-language search (Python + JS + Go)
- Cross-repository discovery
- No exact symbol name known

**Use AST Search when:**
- Finding structural patterns (`async def`, `try/except`)
- Language-specific queries
- Need exact syntax matches
- Performance critical (10ms queries)

**Use Graph Traversal when:**
- Understanding control flow
- Impact analysis ("What breaks if I change this?")
- Dead code detection ("Nothing calls this")
- API usage tracking
- Single repository, known symbol name

**Common workflow:**
1. **Semantic search** to find relevant area
2. **AST search** to understand structure
3. **Graph traversal** to trace execution

---

## Performance Characteristics

### Index Build Time

| Repo Size | Files | Semantic | AST | Graph | Total |
|-----------|-------|----------|-----|-------|-------|
| Small | 100 | 0.2s | 0.1s | 0.1s | 0.4s |
| Medium | 1,000 | 2s | 1s | 1s | 4s |
| Large | 10,000 | 20s | 10s | 10s | 40s |
| praxis-os | 150 | 0.3s | 0.15s | 0.15s | 0.6s |
| python-sdk | 80 | 0.16s | 0.08s | 0.08s | 0.32s |

**Incremental updates:** ~10ms per changed file (parse-once optimization)

### Query Latency

| Operation | Latency | Notes |
|-----------|---------|-------|
| Semantic search | 50-100ms | Vector similarity + reranking |
| AST search | 10-20ms | SQL index scan |
| Graph traversal | 20-50ms | Recursive CTE, depth-dependent |
| Multi-partition semantic | 100-200ms | Parallel queries, merge results |

**Context savings:** 90% reduction (15,000 tokens → 1,500 tokens per query)

### Memory Footprint

| Component | Memory (per 1,000 files) |
|-----------|-------------------------|
| Semantic index (LanceDB) | ~200MB (768-dim vectors) |
| AST index (DuckDB) | ~50MB (node metadata) |
| Graph index (DuckDB) | ~30MB (symbols + edges) |
| Parse cache | ~150MB (temporary) |
| **Total per partition** | **~430MB** |

**Multi-repo:** praxis-os (150 files) + python-sdk (80 files) = ~100MB total

---

## Limitations and Trade-offs

### What Code Intelligence Can't Do

**Cannot track:**
- Dynamic imports (`__import__(module_name)`)
- Reflection/metaprogramming (`getattr(obj, method)()`)
- Runtime polymorphism (which subclass method called?)
- Cross-language calls (Python → JS) without explicit config
- Database queries (SQL strings)
- Network calls (HTTP endpoints)

**Cannot understand:**
- Business logic intent (semantic search helps, but not perfect)
- Performance characteristics (must run profiler)
- Correctness (must run tests)
- Security vulnerabilities (must run SAST tools)

### Accuracy Limitations

**Semantic search:**
- 85-90% relevant in top 5 results
- May miss edge-case synonyms
- Training data bias (CodeBERT trained mostly on Python/Java)

**Graph traversal:**
- ~95% accuracy (misses dynamic calls)
- False negatives (call exists but not detected)
- No false positives (detected calls are real)

### When Traditional Tools Are Better

**Use `grep` when:**
- Exact string known (`grep "TODO"`)
- Text content, not code semantics
- Fastest possible lookup

**Use IDE "Find References" when:**
- Single file/project
- Need real-time updates
- Language server more accurate (type-aware)

**Use debugger when:**
- Need runtime call stack
- Inspect variable values
- Understand execution order

---

## Related Documentation

- [How-To: Using Code Intelligence Effectively](../how-to-guides/using-code-intelligence.md) - Practical patterns and examples
- [Reference: MCP Tools](../reference/mcp-tools.md) - Tool parameters and return values
- [Reference: Configuration](../reference/config-reference.md) - Multi-repo configuration options
- [Explanation: Architecture](./architecture.md) - Overall system design


