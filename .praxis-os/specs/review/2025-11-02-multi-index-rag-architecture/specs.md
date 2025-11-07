# Technical Specifications

**Project:** Multi-Index RAG Architecture  
**Date:** 2025-11-02  
**Version:** 1.0.0

---

## 1. Architecture Overview

### 1.1 System Architecture

**Pattern:** Multi-Index Modular Architecture with Config-Driven Extensibility

```
User Query (via MCP tool)
    ↓
pos_search(content_type="standards", query="...", filters={})
    ↓
IndexManager (Orchestration Layer)
    ↓
├─ content_type="standards" → StandardsIndex
│   ├─ LanceDB Vector Index (semantic search, native)
│   ├─ LanceDB FTS Index (BM25 keyword search, native)
│   └─ LanceDB Scalar Indexes (BTREE/BITMAP for metadata, native)
│       ↓
│   Hybrid Fusion (RRF, k=60) - combines vector + FTS results
│       ↓
│   Re-rank (cross-encoder) - final ordering
│       ↓
│   Return SearchResult[]
│
├─ content_type="code" → CodeIndex
│   ├─ Semantic Search (BGE embeddings on code text)
│   └─ Integration point for ASTIndex
│       ↓
│   Return SearchResult[]
│
└─ content_type="ast" → ASTIndex
    ├─ Tree-sitter parsers (dynamic import per language)
    ├─ AST parsing (extract symbols: functions, classes, methods)
    └─ Symbol index (exact name/signature matching)
        ↓
    Return SearchResult[]
```

### 1.2 Architectural Decisions

**AD-001: Single Database (LanceDB Only)**
- **Decision:** Use LanceDB exclusively for all index types
- **Rationale:** LanceDB provides native FTS (BM25-based), scalar indexes (BTREE/BITMAP), and vector search
- **Alternatives Rejected:** rank-bm25 library + SQLite (unnecessary complexity)
- **Impact:** Simpler architecture, better performance (<100ms at billions of records), fewer dependencies

**AD-002: Config-Driven Architecture**
- **Decision:** All extensibility through `index_config.yaml`, not code changes
- **Rationale:** Add new languages/features by editing config + installing packages
- **Example:** Adding Go support: edit config `languages: [python, go]` + `pip install tree-sitter-go`
- **Impact:** Zero code changes for new languages, user-extensible

**AD-003: Dynamic Tree-sitter Loading**
- **Decision:** Use convention-based dynamic imports (`importlib.import_module(f"tree_sitter_{language}")`)
- **Rationale:** Support all 50+ Tree-sitter languages day 1 without hardcoded lists
- **Alternatives Rejected:** Static language mapping file (frozen in time)
- **Impact:** Graceful degradation when parser unavailable, future-proof

**AD-004: Hybrid Search (Vector + FTS)**
- **Decision:** Combine vector search (semantic) and FTS (keyword) using RRF (k=60)
- **Rationale:** Vector catches concepts, FTS catches terminology - together = better accuracy
- **Impact:** 33% → 50-60% single-query accuracy improvement

**AD-005: Metadata Filtering Pre-Filter**
- **Decision:** Use scalar indexes (BTREE/BITMAP) with SQL WHERE clauses before vector/FTS search
- **Rationale:** Reduces search space dramatically, improves accuracy 50% → 70%+
- **Example:** `WHERE metadata.domain = 'backend'` limits search to backend standards only
- **Impact:** <10ms filtering overhead, significant accuracy improvement

**AD-006: File Locking (Not Blue-Green)**
- **Decision:** Use `fcntl` file locking to prevent concurrent index access
- **Rationale:** Simpler than blue-green deployment, adversarial design (prevent + teach)
- **Teaching Message:** "MCP server holds lock, stop server first or use MCP tool"
- **Impact:** Zero index corruption, teaches correct usage patterns

**AD-007: Zero External API Calls**
- **Decision:** All models/libraries run locally (BGE embeddings, Tree-sitter, LanceDB)
- **Rationale:** Zero-cost constraint, unlimited queries without cost scaling
- **Impact:** Storage <1.5GB, memory <1GB, API cost $0

**AD-008: Unified Search Tool**
- **Decision:** Single `pos_search` MCP tool with explicit `content_type` parameter
- **Rationale:** Clean interface, backward compatible (search_standards delegates to pos_search)
- **Impact:** Zero breaking changes, clear API

### 1.3 Requirements Traceability

| Requirement | Architecture Component | Technology | NFR Met |
|-------------|----------------------|------------|---------|
| FR-001 (Hybrid Search) | StandardsIndex | LanceDB Vector + FTS | NFR-001, NFR-004 |
| FR-002 (Metadata Filtering) | StandardsIndex | LanceDB Scalar Indexes | NFR-001 |
| FR-003 (Semantic Code) | CodeIndex | BGE embeddings | NFR-001, NFR-005 |
| FR-004 (Structural Code) | ASTIndex | Tree-sitter | NFR-001, NFR-005 |
| FR-005 (Dynamic Languages) | ASTIndex | importlib dynamic imports | NFR-007 |
| FR-006 (File Watcher) | AgentOSFileWatcher | watchdog library | NFR-009 |
| FR-007 (Unified Tool) | pos_search MCP tool | IndexManager | NFR-011 |
| FR-008 (LLM Install) | Installation flow | AI agent | NFR-010 |
| FR-009 (Index Safety) | File locking | fcntl | NFR-008 |
| FR-010 (Self-Teaching Config) | index_config.yaml | YAML comments | NFR-007 |
| FR-011 (Zero Cost) | All components | Local models only | NFR-005 |
| FR-012 (Config Extensibility) | Config-driven design | YAML + dynamic imports | NFR-007 |

### 1.4 Technology Stack

| Component | Technology | Version | License | Purpose |
|-----------|-----------|---------|---------|---------|
| **Vector Database** | LanceDB | Latest | Apache 2.0 | All index storage |
| **Vector Search** | LanceDB (native) | - | Apache 2.0 | Semantic search |
| **Full-Text Search** | LanceDB FTS (native, BM25) | - | Apache 2.0 | Keyword search |
| **Scalar Indexes** | LanceDB (BTREE/BITMAP) | - | Apache 2.0 | Metadata filtering |
| **Embeddings** | sentence-transformers | Latest | MIT | BGE-small-en-v1.5 model |
| **Re-ranking** | cross-encoder | Latest | Apache 2.0 | Result reordering |
| **AST Parsing** | Tree-sitter | >=0.21.0 | MIT | Code structure parsing |
| **File Watching** | watchdog | Latest | Apache 2.0 | File system monitoring |
| **Config** | PyYAML | Latest | MIT | YAML parsing |
| **Locking** | fcntl (Python stdlib) | - | PSF | File locking (Unix) |

**Key Insight:** LanceDB provides vector, FTS, and scalar indexes natively - no external rank-bm25 or SQLite needed!

### 1.5 Deployment Architecture

```
.praxis-os/
├── mcp_server/
│   ├── requirements.txt          # Includes tree-sitter-{language} packages
│   ├── server/
│   │   ├── tools/
│   │   │   └── pos_search.py     # Unified search MCP tool
│   │   └── indexes/
│   │       ├── base.py           # BaseIndex abstract class
│   │       ├── index_manager.py  # Orchestration
│   │       ├── standards_index.py # Hybrid search
│   │       ├── code_index.py     # Semantic code search
│   │       └── ast_index.py      # Tree-sitter structural search
│   └── cache/
│       ├── standards/            # LanceDB database
│       ├── code/                 # LanceDB database
│       └── ast/                  # LanceDB database
│
└── config/
    └── index_config.yaml         # Self-teaching configuration

Installation: Isolated venv, no project dependency conflicts
Platform: Unix/Linux/macOS (Windows deferred - fcntl unavailable)
```

---

## 2. Component Design

### 2.1 BaseIndex (Abstract Class)

**File:** `.praxis-os/mcp_server/server/indexes/base.py`

**Responsibility:** Define common interface for all index types, enable polymorphic index management.

**Interface:**

```python
from abc import ABC, abstractmethod
from dataclass import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class SearchResult:
    """Unified result format across all index types."""
    content: str                    # Matched content (chunk text or code snippet)
    file_path: str                  # Source file path
    relevance_score: float          # 0.0-1.0 relevance
    content_type: str               # "standard", "code", "ast"
    metadata: Dict[str, Any]        # {domain, phase, role, language, etc.}
    chunk_id: Optional[str] = None  # For standards: chunk identifier
    line_range: Optional[tuple] = None  # For code: (start_line, end_line)


class BaseIndex(ABC):
    """Abstract base for all index implementations."""
    
    def __init__(self, cache_path: Path, config: dict):
        """Initialize index with cache location and config."""
        self.cache_path = cache_path
        self.config = config
    
    @abstractmethod
    def build(self, source_paths: List[str], force: bool = False):
        """Build or rebuild index from source files."""
        pass
    
    @abstractmethod
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        """Search index and return top n results."""
        pass
    
    @abstractmethod
    def update(self, changed_files: List[str]):
        """Incremental update for changed files only."""
        pass
    
    @abstractmethod
    def delete(self, removed_files: List[str]):
        """Remove entries for deleted files."""
        pass
```

**Dependencies:** None (abstract)

**Error Handling:**
- Subclasses must handle database connection failures
- Return empty list on search failure, log error
- Raise `IndexBuildError` on build failure

### 2.2 IndexManager (Orchestration)

**File:** `.praxis-os/mcp_server/server/indexes/index_manager.py`

**Responsibility:** Orchestrate multiple indexes, route queries to appropriate index, merge results.

**Interface:**

```python
class IndexManager:
    """Config-driven orchestration of multiple indexes."""
    
    def __init__(self, base_path: Path, config_path: Path = None):
        """
        Initialize manager with base path and config.
        
        Args:
            base_path: Root path for all indexes (.praxis-os/)
            config_path: Path to index_config.yaml (optional, uses default)
        """
        self.base_path = base_path
        self.config = self._load_config(config_path)
        self.indexes = self._init_indexes()  # Discover from config
    
    def search(
        self,
        query: str,
        content_type: str,       # "standards", "code", "ast"
        filters: dict = None,    # {domain: "backend", phase: 0}
        n_results: int = 5
    ) -> List[SearchResult]:
        """
        Route query to appropriate index, return merged results.
        
        Args:
            query: Search query string
            content_type: Which index to search
            filters: Metadata filters (optional)
            n_results: Number of results to return
        
        Returns:
            List of SearchResult objects, sorted by relevance
        """
        if content_type not in self.indexes:
            raise ValueError(f"Unknown content_type: {content_type}")
        
        # Route to specific index
        index = self.indexes[content_type]
        results = index.search(query, filters, n_results * 2)  # Get extra for re-ranking
        
        # Re-rank if enabled in config
        if self.config["retrieval"]["rerank"]["enabled"]:
            results = self._rerank(query, results)
        
        return results[:n_results]
    
    def rebuild_all(self, force: bool = False):
        """Rebuild all indexes from scratch."""
        for index_name, index in self.indexes.items():
            print(f"Rebuilding {index_name} index...")
            index.build(source_paths=self.config[index_name]["source_paths"], force=force)
    
    def _init_indexes(self) -> Dict[str, BaseIndex]:
        """
        Initialize indexes based on config.
        
        Config-driven: Reads enabled indexes from YAML, instantiates classes.
        """
        indexes = {}
        
        if self.config["indexes"]["vector"]["enabled"]:
            indexes["standards"] = StandardsIndex(
                cache_path=self.base_path / "cache" / "standards",
                config=self.config["indexes"]
            )
        
        if self.config["indexes"]["code"]["enabled"]:
            indexes["code"] = CodeIndex(
                cache_path=self.base_path / "cache" / "code",
                config=self.config["indexes"]["code"]
            )
            
            indexes["ast"] = ASTIndex(
                cache_path=self.base_path / "cache" / "ast",
                config=self.config["indexes"]["code"]
            )
        
        return indexes
```

**Dependencies:**
- `BaseIndex` (abstract class)
- `StandardsIndex`, `CodeIndex`, `ASTIndex` (concrete implementations)
- `PyYAML` for config loading

**Error Handling:**
- Config load failure → raise `ConfigError` with remediation
- Unknown content_type → raise `ValueError` with available types
- Index init failure → log warning, continue with available indexes

### 2.3 StandardsIndex (Hybrid Search)

**File:** `.praxis-os/mcp_server/server/indexes/standards_index.py`

**Responsibility:** Implement hybrid search (vector + FTS) with metadata filtering for standards corpus.

**Interface:**

```python
import lancedb
from sentence_transformers import SentenceTransformer

class StandardsIndex(BaseIndex):
    """Hybrid search using LanceDB's native capabilities."""
    
    def __init__(self, cache_path: Path, config: dict):
        super().__init__(cache_path, config)
        
        # Single LanceDB connection
        self.db = lancedb.connect(str(cache_path))
        self.table = None  # Initialized in build()
        
        # Load embedding model (BGE-small-en-v1.5 by default)
        self.model = SentenceTransformer(config["vector"]["model"])
    
    def build(self, source_paths: List[str], force: bool = False):
        """
        Build hybrid index: vector + FTS + scalar indexes.
        
        Steps:
        1. Read and chunk markdown files (1000 tokens, 200 overlap)
        2. Generate embeddings via BGE model
        3. Create LanceDB table with vector index
        4. Create FTS index for keyword search
        5. Create scalar indexes for metadata filtering
        """
        # ... chunking logic ...
        
        # Create table with embeddings
        self.table = self.db.create_table(
            "standards",
            data=chunks,  # List[{content, embedding, metadata, file_path, chunk_id}]
            mode="overwrite" if force else "create"
        )
        
        # Create FTS index (BM25-based, LanceDB native!)
        self.table.create_fts_index("content", use_tantivy=False)
        
        # Create scalar indexes for metadata filtering
        self.table.create_scalar_index("metadata.domain", index_type="BTREE")  # High cardinality
        self.table.create_scalar_index("metadata.phase", index_type="BITMAP")  # Low cardinality
        self.table.create_scalar_index("metadata.role", index_type="BITMAP")
    
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        """
        Hybrid search: vector + FTS, merged via RRF, optionally re-ranked.
        
        Steps:
        1. Build WHERE clause from filters (SQL syntax)
        2. Vector search with prefilter
        3. FTS search with same filter
        4. Reciprocal Rank Fusion (k=60)
        5. Return top n
        """
        query_vector = self.model.encode(query)
        where_clause = self._build_where_clause(filters) if filters else None
        
        # 1. Vector search with prefilter (uses scalar indexes!)
        vector_results = (
            self.table.search(query_vector)
            .where(where_clause, prefilter=True)
            .limit(20)
            .to_list()
        )
        
        # 2. FTS (BM25) search with same filter
        fts_query = f"content MATCH '{query}'"
        if where_clause:
            fts_query += f" AND {where_clause}"
        
        fts_results = (
            self.table.search()
            .where(fts_query, fts=True)
            .limit(20)
            .to_list()
        )
        
        # 3. Reciprocal Rank Fusion (RRF with k=60)
        fused = self._reciprocal_rank_fusion(vector_results, fts_results, k=60)
        
        return fused[:n]
    
    def _reciprocal_rank_fusion(self, list1, list2, k=60):
        """
        RRF formula: score = sum(1 / (k + rank_i))
        
        Merges two ranked lists, giving credit to items appearing in both.
        """
        scores = {}
        
        for rank, item in enumerate(list1, start=1):
            item_id = item["chunk_id"]
            scores[item_id] = scores.get(item_id, 0) + (1 / (k + rank))
        
        for rank, item in enumerate(list2, start=1):
            item_id = item["chunk_id"]
            scores[item_id] = scores.get(item_id, 0) + (1 / (k + rank))
        
        # Sort by RRF score descending
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [self._get_item_by_id(item_id) for item_id, score in sorted_items]
```

**Dependencies:**
- `lancedb` (vector database)
- `sentence-transformers` (BGE embeddings)
- `tiktoken` (token counting for chunking)

**Error Handling:**
- Embedding model load failure → log error, fall back to FTS only
- FTS index missing → rebuild automatically
- Empty query → return empty results

### 2.4 CodeIndex (Semantic Code Search)

**File:** `.praxis-os/mcp_server/server/indexes/code_index.py`

**Responsibility:** Enable semantic search over project source code using same BGE model as standards.

**Interface:**

```python
class CodeIndex(BaseIndex):
    """Semantic search over source code using BGE embeddings."""
    
    def __init__(self, cache_path: Path, config: dict):
        super().__init__(cache_path, config)
        
        self.db = lancedb.connect(str(cache_path))
        self.table = None
        self.model = SentenceTransformer(config["vector"]["model"])  # Same model as standards
        self.languages = config["languages"]  # e.g., ["python", "typescript", "go"]
    
    def build(self, source_paths: List[str], force: bool = False):
        """
        Build semantic code index.
        
        Steps:
        1. Discover code files matching language patterns
        2. Chunk code (500 tokens, 50 overlap - smaller than standards)
        3. Generate embeddings
        4. Create LanceDB table with metadata: file_path, language, line_range
        """
        pass
    
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        """
        Semantic code search by concept.
        
        Example: "authentication token handling" → finds code chunks about auth
        """
        query_vector = self.model.encode(query)
        
        where_clause = None
        if filters and "language" in filters:
            where_clause = f"metadata.language = '{filters['language']}'"
        
        results = (
            self.table.search(query_vector)
            .where(where_clause, prefilter=True) if where_clause else
            self.table.search(query_vector)
        ).limit(n).to_list()
        
        return self._to_search_results(results)
```

**Dependencies:**
- `lancedb`
- `sentence-transformers` (same BGE model)
- Language-specific tokenizers (for accurate chunking)

**Error Handling:**
- Unsupported language → log warning, skip file
- Parse error → log warning, index as plain text

### 2.5 ASTIndex (Structural Code Search)

**File:** `.praxis-os/mcp_server/server/indexes/ast_index.py`

**Responsibility:** Enable precise symbol lookup (functions, classes, methods) via Tree-sitter AST parsing.

**Interface:**

```python
import importlib

class ASTIndex(BaseIndex):
    """Structural code search via Tree-sitter AST parsing."""
    
    def __init__(self, cache_path: Path, config: dict):
        super().__init__(cache_path, config)
        
        self.db = lancedb.connect(str(cache_path))
        self.table = None
        self.languages = config["languages"]
        self.parsers = self._load_parsers()  # Dynamic loading
    
    def _load_parsers(self) -> Dict[str, Any]:
        """
        Dynamically load Tree-sitter parsers based on convention.
        
        Convention: tree-sitter-{language} package → tree_sitter_{language} module
        
        Graceful degradation: If parser unavailable, log warning with install instructions.
        """
        parsers = {}
        
        for lang in self.languages:
            try:
                # Convention-based dynamic import
                module_name = f"tree_sitter_{lang.replace('-', '_')}"
                parser_module = importlib.import_module(module_name)
                parsers[lang] = parser_module
                print(f"✅ Loaded Tree-sitter parser for {lang}")
            except ImportError:
                print(f"⚠️  Tree-sitter parser for '{lang}' not installed.")
                print(f"    Install with: pip install tree-sitter-{lang}")
                # Graceful degradation: continue without this parser
        
        return parsers
    
    def build(self, source_paths: List[str], force: bool = False):
        """
        Build AST index.
        
        Steps:
        1. For each language with available parser:
        2.   Parse files into AST
        3.   Extract symbols: function definitions, class definitions, methods
        4.   Store in LanceDB: {symbol_name, symbol_type, file_path, line_range, language}
        """
        pass
    
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        """
        Structural search by symbol name or pattern.
        
        Example: "StateManager class" → finds exact class definition
        """
        # Simple symbol name matching (can be enhanced with fuzzy matching)
        where_clause = f"symbol_name LIKE '%{query}%'"
        
        if filters and "language" in filters:
            where_clause += f" AND language = '{filters['language']}'"
        
        results = (
            self.table.search()
            .where(where_clause)
            .limit(n)
            .to_list()
        )
        
        return self._to_search_results(results)
```

**Dependencies:**
- `tree-sitter` (core library)
- `tree-sitter-{language}` packages (dynamic, per detected language)

**Error Handling:**
- Parser unavailable → log warning, continue without that language
- Parse error → log error, skip file
- Empty AST → log debug, no symbols extracted

### 2.6 AgentOSFileWatcher (Incremental Updates)

**File:** `.praxis-os/mcp_server/server/file_watcher.py`

**Responsibility:** Monitor file system changes, trigger incremental index updates with config-driven patterns and debouncing.

**Interface:**

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AgentOSFileWatcher:
    """Config-driven file system watcher for incremental index updates."""
    
    def __init__(self, config_path: Path, index_manager: IndexManager):
        self.config = self._load_config(config_path)
        self.index_manager = index_manager
        self.observers = []
        self.debounce_timers = {}  # Per content_type debouncing
    
    def start(self):
        """Start watching all configured paths."""
        for content_type, watch_config in self.config["file_watcher"].items():
            observer = Observer()
            handler = self._create_handler(content_type, watch_config)
            
            for path in watch_config["paths"]:
                observer.schedule(handler, path, recursive=True)
            
            observer.start()
            self.observers.append(observer)
    
    def _create_handler(self, content_type: str, config: dict):
        """
        Create file system event handler with config-driven patterns.
        
        Config structure:
          standards:
            patterns: ["*.md"]
            exclude: ["**/node_modules/**", "**/__pycache__/**"]
            debounce_seconds: 2
        """
        class ConfigDrivenHandler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                file_path = event.src_path
                
                # Check if matches patterns
                if self._matches_patterns(file_path, config["patterns"], config["exclude"]):
                    # Debounce: schedule rebuild after N seconds
                    self._schedule_rebuild(content_type, config["debounce_seconds"])
        
        return ConfigDrivenHandler()
    
    def _schedule_rebuild(self, content_type: str, debounce_seconds: int):
        """
        Debounce rebuilds per content type.
        
        If multiple files change rapidly, only trigger one rebuild after quiet period.
        """
        if content_type in self.debounce_timers:
            self.debounce_timers[content_type].cancel()
        
        timer = Timer(debounce_seconds, lambda: self._trigger_rebuild(content_type))
        self.debounce_timers[content_type] = timer
        timer.start()
    
    def _trigger_rebuild(self, content_type: str):
        """Trigger incremental index rebuild."""
        print(f"🔄 Rebuilding {content_type} index (file changes detected)")
        index = self.index_manager.indexes[content_type]
        index.update(changed_files=self._get_changed_files(content_type))
```

**Dependencies:**
- `watchdog` (file system monitoring)
- `fnmatch` (pattern matching)

**Error Handling:**
- File read failure → log warning, skip file
- Index update failure → log error, retry on next change
- Pattern match error → log error, fall back to all files

### 2.7 pos_search MCP Tool

**File:** `.praxis-os/mcp_server/server/tools/pos_search.py`

**Responsibility:** Unified MCP tool for searching all content types (standards, code, AST).

**Interface:**

```python
@server.tool()
async def pos_search(
    content_type: str,              # "standards", "code", "ast"
    query: str,                     # Search query
    filters: dict = None,           # {domain: "backend", language: "python"}
    n_results: int = 5              # Number of results
) -> dict:
    """
    Unified search across all indexed content types.
    
    Args:
        content_type: Which index to search
          - "standards": Project standards/documentation
          - "code": Semantic code search (by concept)
          - "ast": Structural code search (by symbol name)
        query: Search query string
        filters: Metadata filters (optional)
          - For standards: {domain, phase, role}
          - For code/ast: {language}
        n_results: Number of results to return (default 5)
    
    Returns:
        {
            "results": [
                {
                    "content": "...",
                    "file_path": "...",
                    "relevance_score": 0.95,
                    "metadata": {...},
                    "chunk_id": "..." (standards only),
                    "line_range": [10, 25] (code/ast only)
                },
                ...
            ],
            "count": 5,
            "content_type": "standards"
        }
    """
    index_manager = get_index_manager()  # Singleton
    
    try:
        results = index_manager.search(
            query=query,
            content_type=content_type,
            filters=filters,
            n_results=n_results
        )
        
        return {
            "results": [r.to_dict() for r in results],
            "count": len(results),
            "content_type": content_type
        }
    
    except ValueError as e:
        # Unknown content_type
        return {
            "error": str(e),
            "available_types": ["standards", "code", "ast"]
        }
    except Exception as e:
        # General search failure
        return {
            "error": f"Search failed: {str(e)}",
            "results": [],
            "count": 0
        }
```

**Backward Compatibility:**

```python
# Legacy search_standards tool delegates to pos_search
@server.tool()
async def search_standards(query: str, n_results: int = 5) -> dict:
    """Legacy tool - delegates to pos_search for backward compatibility."""
    return await pos_search(
        content_type="standards",
        query=query,
        filters=None,
        n_results=n_results
    )
```

---

## 3. API Design

### 3.1 pos_search MCP Tool

**Tool Name:** `pos_search`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `content_type` | string | Yes | - | Index to search: "standards", "code", "ast" |
| `query` | string | Yes | - | Search query text |
| `filters` | object | No | {} | Metadata filters (domain, phase, role, language) |
| `n_results` | integer | No | 5 | Number of results to return (1-50) |

**Response Schema:**

```json
{
  "results": [
    {
      "content": "string",           // Matched content
      "file_path": "string",         // Source file
      "relevance_score": "float",    // 0.0-1.0
      "content_type": "string",      // "standard", "code", "ast"
      "metadata": {                  // Content-type specific
        "domain": "string",          // standards only
        "phase": "integer",          // standards only
        "role": "string",            // standards only
        "language": "string",        // code/ast only
        ...
      },
      "chunk_id": "string | null",   // standards only
      "line_range": "[int, int] | null"  // code/ast only
    }
  ],
  "count": "integer",
  "content_type": "string"
}
```

**Error Response:**

```json
{
  "error": "string",
  "available_types": ["standards", "code", "ast"],
  "results": [],
  "count": 0
}
```

**Example Usage:**

```python
# Standards search with metadata filter
await pos_search(
    content_type="standards",
    query="how to create workflows",
    filters={"domain": "development", "phase": 0},
    n_results=5
)

# Code search by concept
await pos_search(
    content_type="code",
    query="authentication token validation",
    filters={"language": "python"},
    n_results=10
)

# AST search by symbol name
await pos_search(
    content_type="ast",
    query="StateManager class",
    filters={"language": "typescript"},
    n_results=1
)
```

### 3.2 Internal APIs

**IndexManager.search()**

```python
def search(
    self,
    query: str,
    content_type: str,
    filters: dict = None,
    n_results: int = 5
) -> List[SearchResult]:
    """
    Route query to appropriate index.
    
    Raises:
        ValueError: If content_type unknown
        IndexError: If index not initialized
    """
```

**BaseIndex.search()**

```python
@abstractmethod
def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
    """
    Search this index.
    
    Returns:
        List of SearchResult objects, sorted by relevance descending
    """
```

### 3.3 SearchResult DTO

```python
@dataclass
class SearchResult:
    """Data transfer object for search results."""
    content: str                    # Matched content
    file_path: str                  # Source file path
    relevance_score: float          # 0.0-1.0
    content_type: str               # "standard", "code", "ast"
    metadata: Dict[str, Any]        # Content-specific metadata
    chunk_id: Optional[str] = None  # Standards: chunk identifier
    line_range: Optional[tuple] = None  # Code/AST: (start_line, end_line)
    
    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict for MCP response."""
        return {
            "content": self.content,
            "file_path": self.file_path,
            "relevance_score": self.relevance_score,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "chunk_id": self.chunk_id,
            "line_range": list(self.line_range) if self.line_range else None
        }
```

### 3.4 FilterDict Type

```python
# Type alias for clarity
FilterDict = Dict[str, Union[str, int, List[str], List[int]]]

# Examples:
# {"domain": "backend"}                      # Single value
# {"domain": ["backend", "frontend"]}       # Multiple values (OR)
# {"domain": "backend", "phase": 0}         # Multiple fields (AND)
# {"language": "python"}                    # For code/ast
```

### 3.5 Error Handling Strategy

**Error Types:**

1. **User Input Errors** (4xx equivalent)
   - Unknown content_type → `ValueError` → Return error with available types
   - Invalid query (empty) → Return empty results
   - Invalid filters → Ignore invalid fields, log warning

2. **System Errors** (5xx equivalent)
   - Index not found → `IndexError` → Return error, suggest rebuild
   - Database connection failure → Log error, return cached results or error
   - Embedding model failure → Fall back to FTS only, log warning

3. **Graceful Degradation**
   - Tree-sitter parser unavailable → Log warning, skip that language
   - FTS index missing → Use vector search only
   - Re-ranker unavailable → Skip re-ranking step

**Error Logging:**

```python
import logging

logger = logging.getLogger("praxis_os.indexes")

# Log levels:
# ERROR: System failures (database down, critical errors)
# WARNING: Degraded functionality (parser missing, fallback used)
# INFO: Normal operations (index rebuild, search complete)
# DEBUG: Detailed tracing (query vectors, fusion scores)
```

### 3.6 API Documentation

**MCP Tool Metadata:**

```python
@server.tool(
    name="pos_search",
    description="Unified search across standards, code, and AST indexes",
    parameters={
        "content_type": {
            "type": "string",
            "enum": ["standards", "code", "ast"],
            "description": "Which index to search"
        },
        "query": {
            "type": "string",
            "description": "Search query text"
        },
        "filters": {
            "type": "object",
            "description": "Optional metadata filters",
            "properties": {
                "domain": {"type": "string"},
                "phase": {"type": "integer"},
                "role": {"type": "string"},
                "language": {"type": "string"}
            }
        },
        "n_results": {
            "type": "integer",
            "minimum": 1,
            "maximum": 50,
            "default": 5,
            "description": "Number of results to return"
        }
    },
    required=["content_type", "query"]
)
```

---

## 4. Data Models

### 4.1 SearchResult Dataclass

```python
@dataclass
class SearchResult:
    content: str
    file_path: str
    relevance_score: float
    content_type: str
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
    line_range: Optional[tuple] = None
```

**Business Rules:**
- `relevance_score` must be 0.0-1.0
- `content_type` must be "standard", "code", or "ast"
- `chunk_id` required for standards, None for code/ast
- `line_range` required for code/ast, None for standards
- `metadata` structure varies by content_type

### 4.2 IndexConfig Dataclass

```python
@dataclass
class IndexConfig:
    """Configuration for multi-index RAG system."""
    
    # Vector search config
    vector: VectorConfig
    
    # FTS config
    fts: FTSConfig
    
    # Metadata filtering config
    metadata: MetadataConfig
    
    # Code search config
    code: CodeConfig
    
    # Retrieval config (hybrid, re-ranking)
    retrieval: RetrievalConfig
    
    # File watcher config
    file_watcher: Dict[str, WatcherConfig]
    
    # Monitoring config
    monitoring: MonitoringConfig


@dataclass
class VectorConfig:
    enabled: bool
    model: str  # "BAAI/bge-small-en-v1.5"
    source_paths: List[str]
    file_patterns: List[str]
    chunk_size: int  # 1000 for standards, 500 for code
    chunk_overlap: int  # 200 for standards, 50 for code


@dataclass
class CodeConfig:
    enabled: bool
    languages: List[str]  # ["python", "typescript", "go"]
    source_paths: List[str]
    file_patterns: Dict[str, List[str]]  # {python: ["*.py"], typescript: ["*.ts"]}
    exclude_patterns: List[str]  # ["**/node_modules/**", "**/__pycache__/**"]
```

### 4.3 LanceDB Table Schemas

**Table 1: praxis_os_standards**

```python
# Standards index table schema
{
    "chunk_id": "string",            # Unique identifier (file_path:chunk_idx)
    "content": "string",             # Chunk text content
    "embedding": "vector<float>[384]",  # BGE-small-en-v1.5 embedding (384 dims)
    "file_path": "string",           # Source file path
    "metadata": {                    # Nested object
        "domain": "string",          # "backend", "frontend", "qa", "devops"
        "phase": "int",              # 0-8 (workflow phase)
        "role": "string",            # "user", "orchestrator", "specialist"
        "tags": "list<string>",      # ["workflow", "testing", "documentation"]
        "created": "timestamp"       # File creation date
    }
}

# Indexes created:
# - Vector index (default on `embedding` column)
# - FTS index on `content` column (BM25-based)
# - BTREE scalar index on `metadata.domain` (high cardinality)
# - BITMAP scalar index on `metadata.phase` (low cardinality, 0-8)
# - BITMAP scalar index on `metadata.role` (low cardinality)
```

**Table 2: praxis_os_code_semantic**

```python
# Semantic code search table schema
{
    "chunk_id": "string",            # file_path:line_start:line_end
    "content": "string",             # Code chunk text
    "embedding": "vector<float>[384]",  # Same BGE model as standards
    "file_path": "string",           # Source file path
    "line_range": "struct<start: int, end: int>",  # Line range in file
    "metadata": {
        "language": "string",        # "python", "typescript", "go"
        "symbols": "list<string>",   # Function/class names in chunk
        "complexity": "int"          # Cyclomatic complexity (optional)
    }
}

# Indexes created:
# - Vector index (default on `embedding` column)
# - BTREE scalar index on `metadata.language`
```

**Table 3: praxis_os_code_ast**

```python
# AST structural search table schema
{
    "symbol_id": "string",           # Unique identifier
    "symbol_name": "string",         # Function/class name
    "symbol_type": "string",         # "function", "class", "method", "variable"
    "file_path": "string",           # Source file path
    "line_range": "struct<start: int, end: int>",  # Definition location
    "signature": "string",           # Full signature (for functions)
    "metadata": {
        "language": "string",        # "python", "typescript", "go"
        "parent_symbol": "string",   # For methods: parent class name
        "is_exported": "bool"        # Public vs private
    }
}

# Indexes created:
# - BTREE index on `symbol_name` (for LIKE queries)
# - BITMAP index on `symbol_type` (low cardinality)
# - BTREE index on `metadata.language`
```

### 4.4 Data Lifecycle

**Standards Index:**
1. **Ingestion:** Markdown files read → chunked (1000 tokens, 200 overlap) → embedded → stored
2. **Update:** File modified → re-chunk → re-embed → replace chunks → rebuild FTS
3. **Query:** User query → embed query → vector search + FTS → merge (RRF) → re-rank → return
4. **Deletion:** File removed → delete all chunks for that file_path

**Code Index:**
1. **Ingestion:** Code files discovered → chunked (500 tokens, 50 overlap) → embedded → stored
2. **AST Parsing:** Tree-sitter parses → extract symbols → store in ast table
3. **Update:** File modified → re-chunk + re-parse → update both tables
4. **Query (Semantic):** Query → embed → vector search → return
5. **Query (Structural):** Query → symbol name matching (LIKE) → return exact definitions

### 4.5 Storage Estimates

**Standards Index (500 standards, ~500KB avg):**
- Raw text: ~250MB
- Embeddings (384-dim float32): ~150MB
- FTS index: ~50MB
- Metadata + overhead: ~50MB
- **Total: ~500MB**

**Code Semantic Index (100K lines, ~50 bytes/line):**
- Raw code chunks: ~5MB
- Embeddings: ~200MB
- Metadata + overhead: ~50MB
- **Total: ~255MB**

**Code AST Index (100K lines, ~10 symbols/100 lines):**
- Symbol entries (10K symbols * 1KB): ~10MB
- Indexes: ~10MB
- **Total: ~20MB**

**Grand Total: ~775MB < 1.5GB target ✅**

### 4.6 Performance Estimates

**Query Latency (Local Hardware):**
- Vector search (10K standards): ~50ms
- FTS search (10K standards): ~20ms
- Scalar index filter: ~5ms
- RRF merge: ~5ms
- Re-ranking (top 10): ~20ms
- **Total hybrid search: ~100ms < 200ms target ✅**

**Index Build Time (Initial):**
- Standards (500 docs): ~5 minutes
- Code semantic (100K lines): ~10 minutes
- Code AST (100K lines): ~5 minutes
- **Total: ~20 minutes (acceptable for install)**

**Incremental Update (Single File):**
- Re-chunk + re-embed: ~2 seconds
- Database write: ~1 second
- **Total: ~3 seconds < 5 seconds target ✅**

---

## 5. Security Design

### 5.1 Threat Model

**Threat 1: Concurrent Index Corruption**
- **Attack:** Manual index rebuild while MCP server is running
- **Impact:** Index corruption, search failures
- **Mitigation:** File locking (fcntl) prevents concurrent write access
- **Detection:** Lock acquisition failure
- **Response:** Teaching message: "MCP server holds lock, stop server first or use MCP tool"

**Threat 2: Malicious Standards Injection**
- **Attack:** Inject malicious content into standards to poison RAG results
- **Impact:** AI agent receives incorrect guidance
- **Mitigation:** Standards corpus controlled by user (local files)
- **Detection:** N/A (trusted input assumption)
- **Response:** User vets all standards content

**Threat 3: Path Traversal in File Operations**
- **Attack:** Supply `../../etc/passwd` as file_path in filters
- **Impact:** Read arbitrary files
- **Mitigation:** Validate all file paths against allowed source_paths
- **Detection:** Path validation failure
- **Response:** Reject query with error

**Threat 4: Resource Exhaustion (DoS)**
- **Attack:** Large query with n_results=10000
- **Impact:** Memory/CPU exhaustion
- **Mitigation:** Cap n_results at 50, timeout queries >30s
- **Detection:** Parameter validation
- **Response:** Return error

**Threat 5: Dependency Vulnerabilities**
- **Attack:** Exploit vulnerability in Tree-sitter or LanceDB
- **Impact:** Code execution, data corruption
- **Mitigation:** Pin dependency versions, monitor CVEs
- **Detection:** Dependency scanning (e.g., pip-audit)
- **Response:** Update vulnerable packages

### 5.2 File System Security

**Index Directory Permissions:**
```bash
.praxis-os/cache/
├── standards/  (rwx for user only, 700)
├── code/       (rwx for user only, 700)
└── ast/        (rwx for user only, 700)
```

**Config File Permissions:**
```bash
.praxis-os/config/index_config.yaml  (rw- for user only, 600)
```

**File Locking:**
```python
import fcntl

def acquire_lock(file_path: Path, timeout: int = 5) -> bool:
    """
    Acquire exclusive lock on index file.
    
    Returns:
        True if lock acquired, False if timeout
    
    Raises:
        BlockingIOError: If another process holds lock
    """
    lock_file = file_path / ".index.lock"
    lock_fd = open(lock_file, 'w')
    
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        # Lock held by another process
        print(f"⚠️  Index lock held by another process")
        print(f"    MCP server may be running")
        print(f"    Stop server first: kill $(cat .praxis-os/mcp_server.pid)")
        print(f"    Or use MCP tool: pos_rebuild_index()")
        return False
```

### 5.3 Concurrency Protection

**Read-Write Locking:**
- **MCP Server:** Acquires shared read lock on startup
- **Manual Rebuild:** Requires exclusive write lock (blocks if server running)
- **File Watcher:** Uses same shared lock as server (concurrent reads OK)

**Race Condition Prevention:**
- **Index Updates:** Atomic writes (write to temp, move to final location)
- **Config Reloads:** Reload config before each index rebuild (avoid stale config)

### 5.4 Input Validation

**Query Validation:**
```python
def validate_query(query: str) -> str:
    """
    Validate and sanitize query input.
    
    Rules:
    - Max length: 1000 characters
    - No null bytes
    - Trim whitespace
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    if len(query) > 1000:
        raise ValueError("Query too long (max 1000 characters)")
    
    if '\x00' in query:
        raise ValueError("Query contains invalid null byte")
    
    return query.strip()
```

**Filter Validation:**
```python
def validate_filters(filters: dict, content_type: str) -> dict:
    """
    Validate filter structure and values.
    
    Rules:
    - Only allowed keys for content_type
    - Values must be strings, ints, or lists thereof
    """
    allowed_keys = {
        "standards": ["domain", "phase", "role"],
        "code": ["language"],
        "ast": ["language", "symbol_type"]
    }
    
    if content_type not in allowed_keys:
        raise ValueError(f"Unknown content_type: {content_type}")
    
    for key in filters:
        if key not in allowed_keys[content_type]:
            # Ignore unknown keys, don't raise (graceful degradation)
            print(f"⚠️  Ignoring unknown filter key: {key}")
    
    return {k: v for k, v in filters.items() if k in allowed_keys[content_type]}
```

**Path Validation:**
```python
def validate_file_path(file_path: str, allowed_roots: List[Path]) -> Path:
    """
    Validate file path is within allowed roots.
    
    Prevents path traversal attacks.
    """
    path = Path(file_path).resolve()  # Resolve symlinks, ..
    
    for root in allowed_roots:
        if path.is_relative_to(root):
            return path
    
    raise ValueError(f"File path not in allowed directories: {file_path}")
```

### 5.5 Dependency Security

**Pinned Versions:**
```txt
# requirements.txt
lancedb==0.13.0
sentence-transformers==2.5.1
tree-sitter==0.21.3
watchdog==4.0.0
PyYAML==6.0.1
```

**License Compliance:**
- LanceDB: Apache 2.0 ✅
- sentence-transformers: MIT ✅
- tree-sitter: MIT ✅
- watchdog: Apache 2.0 ✅
- PyYAML: MIT ✅

**Vulnerability Scanning:**
```bash
# Run during CI/CD
pip-audit --requirement requirements.txt --fix
```

### 5.6 Code Security

**SQL Injection Prevention:**
```python
# BAD: String interpolation
where_clause = f"domain = '{filters['domain']}'"  # SQL injection risk!

# GOOD: Parameterized queries or validated enum
ALLOWED_DOMAINS = {"backend", "frontend", "qa", "devops"}
if filters['domain'] not in ALLOWED_DOMAINS:
    raise ValueError(f"Invalid domain: {filters['domain']}")
where_clause = f"domain = '{filters['domain']}'"  # Safe (validated enum)
```

**Path Traversal Prevention:**
```python
# BAD: Unvalidated path
content = open(file_path).read()  # Path traversal risk!

# GOOD: Validated against allowed roots
validated_path = validate_file_path(file_path, allowed_roots=[Path(".praxis-os/standards")])
content = validated_path.read_text()
```

**Dynamic Import Safety:**
```python
# BAD: Arbitrary module import
module = importlib.import_module(user_input)  # Code injection risk!

# GOOD: Convention-based with validation
ALLOWED_LANGUAGES = {"python", "typescript", "javascript", "go", "rust"}
if language not in ALLOWED_LANGUAGES:
    raise ValueError(f"Unsupported language: {language}")
module_name = f"tree_sitter_{language}"  # Safe (validated language)
module = importlib.import_module(module_name)
```

### 5.7 Security Monitoring

**Logging Security Events:**
```python
# Failed lock acquisition (potential manual rebuild attempt)
logger.warning(f"Index lock acquisition failed: {file_path}")

# Path traversal attempt
logger.error(f"Path validation failed: {file_path}")

# Invalid input
logger.warning(f"Invalid filter key: {key} for content_type: {content_type}")
```

**Metrics:**
- Lock acquisition failures per hour
- Path validation failures per hour
- Invalid input rejections per hour

### 5.8 Platform-Specific Security

**Unix/Linux/macOS:**
- fcntl file locking available ✅
- File permissions enforced by OS ✅

**Windows:**
- fcntl unavailable ❌
- Deferred: Use msvcrt file locking (LockFileEx)
- File permissions less granular

---

## 6. Performance Design

### 6.1 Performance Targets

| Metric | Target | Measured Against |
|--------|--------|------------------|
| Standards hybrid search latency (p95) | <200ms | 500+ standards corpus |
| Code semantic search latency (p95) | <200ms | 100K lines of code |
| AST structural search latency (p95) | <100ms | 10K symbols |
| Metadata filter overhead | <10ms | Any corpus size |
| Index build time (initial) | <20 minutes | 500 standards + 100K code |
| Incremental update (single file) | <5 seconds | Any file size <1MB |
| Memory usage (active query) | <1GB | Concurrent queries |
| Storage (total indexes) | <1.5GB | 500 standards + 100K code |

### 6.2 Query Optimization

**Vector Search Optimization:**
```python
# Use prefilter for metadata (faster than post-filter)
results = table.search(query_vector).where(where_clause, prefilter=True).limit(n)

# NOT: Post-filter (scans all results, then filters)
results = table.search(query_vector).limit(n * 10).filter(where_clause)
```

**FTS Optimization:**
```python
# Combine FTS with metadata filter in single query
fts_query = f"content MATCH '{query}' AND metadata.domain = 'backend'"
results = table.search().where(fts_query, fts=True).limit(n)

# NOT: Separate FTS + filter (two table scans)
fts_results = table.search().where(f"content MATCH '{query}'", fts=True).limit(n * 10)
filtered = [r for r in fts_results if r['metadata']['domain'] == 'backend']
```

**Metadata Filter Optimization:**
```python
# Use BTREE indexes for high-cardinality fields (domain: many values)
table.create_scalar_index("metadata.domain", index_type="BTREE")

# Use BITMAP indexes for low-cardinality fields (phase: 0-8 only)
table.create_scalar_index("metadata.phase", index_type="BITMAP")
```

**Re-Ranking Optimization:**
```python
# Only re-rank top N results (not all)
hybrid_results = rrf(vector_results, fts_results)[:20]  # Get top 20
reranked = cross_encoder.rerank(query, hybrid_results)  # Re-rank only these 20
return reranked[:5]  # Return top 5
```

### 6.3 Index Build Optimization

**Parallel Chunking:**
```python
from multiprocessing import Pool

def chunk_file(file_path: str) -> List[Chunk]:
    """Chunk a single file."""
    # ... chunking logic ...

# Parallel processing of files
with Pool(processes=os.cpu_count()) as pool:
    all_chunks = pool.map(chunk_file, file_paths)
```

**Batch Embedding:**
```python
# Embed chunks in batches (GPU utilization)
BATCH_SIZE = 32

for i in range(0, len(chunks), BATCH_SIZE):
    batch = chunks[i:i+BATCH_SIZE]
    batch_texts = [c.content for c in batch]
    embeddings = model.encode(batch_texts, batch_size=BATCH_SIZE)
    # ... store embeddings ...
```

**Incremental Index Building:**
```python
# For large corpora, build index in stages
# Stage 1: Add all documents without indexes
table = db.create_table("standards", data=all_chunks, mode="overwrite")

# Stage 2: Create indexes after all data loaded (faster than per-insert indexing)
table.create_fts_index("content")
table.create_scalar_index("metadata.domain")
```

### 6.4 Memory Optimization

**Streaming File Reading:**
```python
# BAD: Load entire file into memory
content = Path(file_path).read_text()  # May be GB for large files

# GOOD: Stream chunks
def stream_chunks(file_path: Path, chunk_size: int):
    with open(file_path) as f:
        buffer = ""
        for line in f:
            buffer += line
            if len(buffer) >= chunk_size:
                yield buffer[:chunk_size]
                buffer = buffer[chunk_size:]
        if buffer:
            yield buffer
```

**Lazy Model Loading:**
```python
class StandardsIndex:
    def __init__(self, ...):
        self._model = None  # Don't load until first search
    
    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.config["model"])
        return self._model
```

**Result Streaming:**
```python
# Return results as iterator for large result sets
def search(self, query: str, n: int) -> Iterator[SearchResult]:
    for result in self.table.search(query_vector).limit(n):
        yield SearchResult.from_lancedb(result)
```

### 6.5 Storage Optimization

**Chunking Strategy:**
```python
# Standards: Larger chunks (less overlap) for better compression
STANDARDS_CHUNK_SIZE = 1000
STANDARDS_OVERLAP = 200

# Code: Smaller chunks (focused) for precise search
CODE_CHUNK_SIZE = 500
CODE_OVERLAP = 50
```

**Embedding Precision:**
```python
# Use float16 instead of float32 for embeddings (50% storage savings)
# LanceDB supports float16 natively
embeddings = model.encode(texts, output_dtype="float16")
```

**LanceDB Compaction:**
```python
# Periodically compact LanceDB tables (remove fragmentation)
table.compact()  # Reduces storage, improves query performance
```

### 6.6 Monitoring

**Query Performance Metrics:**
```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "query_latency": [],
            "query_count": 0,
            "cache_hits": 0
        }
    
    def record_query(self, start_time: float, cache_hit: bool):
        latency = time.time() - start_time
        self.metrics["query_latency"].append(latency)
        self.metrics["query_count"] += 1
        if cache_hit:
            self.metrics["cache_hits"] += 1
    
    def report(self):
        latencies = self.metrics["query_latency"]
        return {
            "p50": np.percentile(latencies, 50),
            "p95": np.percentile(latencies, 95),
            "p99": np.percentile(latencies, 99),
            "avg": np.mean(latencies),
            "count": self.metrics["query_count"],
            "cache_hit_rate": self.metrics["cache_hits"] / self.metrics["query_count"]
        }
```

**Resource Usage:**
```python
import psutil

def get_resource_usage():
    process = psutil.Process()
    return {
        "memory_mb": process.memory_info().rss / 1024 / 1024,
        "cpu_percent": process.cpu_percent(),
        "disk_io": psutil.disk_io_counters()
    }
```

### 6.7 Scaling Strategy

**Vertical Scaling (Current):**
- Single machine, local indexes
- Suitable for per-project installations (500 standards, 100K code)
- Memory: 1GB active, 2GB recommended
- Storage: 1.5GB indexes, 10GB recommended total

**Horizontal Scaling (Future):**
- Shard indexes by content_type or metadata.domain
- Distribute shards across multiple nodes
- Query fan-out and merge results
- NOT NEEDED for current single-user, per-project use case

**Caching Strategy:**
- Query result caching (LRU cache, 100 queries)
- Embedding caching (avoid re-embedding common queries)
- Model caching (keep embedding model in memory)

### 6.8 Performance Testing

**Load Testing:**
```python
# Simulate 100 concurrent queries
import asyncio

async def run_query(query: str):
    start = time.time()
    result = await pos_search(content_type="standards", query=query)
    return time.time() - start

async def load_test(num_queries: int = 100):
    queries = ["query 1", "query 2", ...]  # 100 varied queries
    latencies = await asyncio.gather(*[run_query(q) for q in queries])
    
    print(f"p95 latency: {np.percentile(latencies, 95):.2f}ms")
    print(f"Max latency: {max(latencies):.2f}ms")
```

**Acceptance Criteria:**
- p95 latency < 200ms under 100 concurrent queries ✅
- Memory < 1GB during load test ✅
- No index corruption after 1000 queries ✅

---

This completes the comprehensive technical specifications for the Multi-Index RAG Architecture.

