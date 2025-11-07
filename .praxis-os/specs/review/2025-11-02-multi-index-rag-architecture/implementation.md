# Implementation Guidance

**Project:** Multi-Index RAG Architecture  
**Date:** 2025-11-02  
**Audience:** AI agents implementing the spec

---

## 1. Implementation Philosophy

### Core Principles

**1. Config-Driven Dynamic Logic**
- Config declares intent, code discovers capability at runtime
- **Anti-pattern:** Hardcoded lists in code
- **Correct pattern:** Config + dynamic imports + graceful degradation
- Reference: `.praxis-os/standards/development/config-driven-dynamic-logic.md`

**2. Incremental Delivery (Phase-Gated)**
- Each phase delivers measurable value
- Foundation (Phase 1) enables all other phases
- Phases 2-3 are critical path, Phases 4-7 can run in parallel

**3. Test-First Development**
- Unit tests: ≥80% coverage (BLOCKING quality gate)
- Integration tests: ≥60% coverage
- Systematic test generation (follow `test-generation-js-ts` workflow pattern)

**4. Graceful Degradation**
- Missing Tree-sitter parser → log warning, continue without
- FTS index unavailable → fall back to vector-only search
- Re-ranker disabled → skip re-ranking step

**5. Zero Breaking Changes**
- Existing `search_standards` API must work unchanged
- RAGEngine delegates to IndexManager (transparent refactor)
- Backward compatibility tests must pass

---

## 2. Implementation Order

Follow this strict sequence (see `tasks.md` for detailed breakdown):

```
Phase 1: Foundation (2-3 hours) → REQUIRED FIRST
    ↓
Phase 2: Hybrid Search (1.5-2 hours) → Builds on Phase 1
    ↓
Phase 3: Metadata Filtering (2-2.5 hours) → Builds on Phase 2
    ↓
Phase 4-7 (PARALLEL): Code Search, File Watcher, Installation
    ↓
Phase 8: Integration & Testing (1-2 hours) → Final validation
```

**Critical Path:** Phase 1 → 2 → 3 → 8 (7.5-10 hours minimum)

---

## 3. Code Patterns (COPIED from Design Document)

### Pattern 1: BaseIndex Abstract Class

**File:** `.praxis-os/mcp_server/server/indexes/base.py`

```python
# COPIED from design document
# indexes/base.py

from abc import ABC, abstractmethod
from dataclass import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path

@dataclass
class SearchResult:
    """Unified result format across all index types."""
    content: str
    file_path: str
    relevance_score: float
    content_type: str  # "standard", "code", "dependency"
    metadata: Dict[str, Any]
    chunk_id: Optional[str] = None
    line_range: Optional[tuple] = None  # For code: (start, end)


class BaseIndex(ABC):
    """Abstract base for all index implementations."""
    
    @abstractmethod
    def build(self, source_paths: List[str], force: bool = False):
        """Build or rebuild index."""
        pass
    
    @abstractmethod
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        """Search index."""
        pass
    
    @abstractmethod
    def update(self, changed_files: List[str]):
        """Incremental update."""
        pass
```

**Why:** Single abstraction, multiple implementations. Add new indexes without touching orchestration.

---

### Pattern 2: IndexManager Orchestration

**File:** `.praxis-os/mcp_server/server/indexes/index_manager.py`

```python
# COPIED from design document
# index_manager.py

from pathlib import Path
from typing import List, Dict

class IndexManager:
    """Config-driven orchestration of multiple indexes."""
    
    def __init__(self, base_path: Path, config_path: Path = None):
        self.config = self._load_config(config_path)
        self.indexes = self._init_indexes()  # From config
    
    def search(
        self,
        query: str,
        content_types: List[str],  # ["standards"] or ["code"]
        filters: dict = None,
        n_results: int = 5
    ) -> List[SearchResult]:
        """Route to appropriate index(es), merge results."""
        results = []
        
        for content_type in content_types:
            if content_type in self.indexes:
                # Each index handles its own hybrid search (FTS + vector internally)
                idx_results = self.indexes[content_type].search(query, filters, n_results * 2)
                results.extend(idx_results)
        
        # Re-rank if enabled (across all content types)
        if self.config["retrieval"]["rerank"]["enabled"]:
            results = self._rerank(query, results)
        
        return results[:n_results]
```

**Why:** Single orchestration point. Config-driven behavior. Easy to extend.

---

### Pattern 3: Config-Driven Dynamic Loading (Tree-sitter)

**File:** `.praxis-os/mcp_server/server/indexes/ast_index.py`

```python
# COPIED from config-driven-dynamic-logic.md standard
import importlib
import logging

logger = logging.getLogger(__name__)

def try_import_parser(language_name: str):
    """Dynamically import Tree-sitter language parser based on convention."""
    try:
        # e.g., "python" -> "tree_sitter_python"
        module_name = f"tree_sitter_{language_name.replace('-', '_')}"
        return importlib.import_module(module_name)
    except ImportError:
        logger.warning(f"Tree-sitter parser for '{language_name}' not installed. "
                       f"Install with 'pip install tree-sitter-{language_name}' for full support.")
        return None

def process_file(file_path: str, language: str):
    """Process file using dynamic parser or fallback."""
    if parser_module := try_import_parser(language):
        logger.info(f"Using Tree-sitter parser for {language}")
        # Use parser_module to parse AST, extract symbols, etc.
        return parser_module.parse(file_path)
    else:
        logger.info(f"No Tree-sitter parser for {language}, using fallback logic.")
        # Fallback to keyword-based parsing or simple text processing
        return fallback_process(file_path)
```

**Why:** 
- **Future-proof:** Supports all 50+ Tree-sitter languages day 1
- **User-extensible:** User adds language to config + `pip install tree-sitter-{lang}`, no prAxIs OS code changes
- **Zero maintenance:** No frozen mapping file
- **Graceful degradation:** System continues with warning if parser unavailable

---

### Pattern 4: File Locking (Adversarial Design)

**File:** `.praxis-os/mcp_server/server/indexes/index_manager.py`

```python
import fcntl

def acquire_lock(file_path: Path, timeout: int = 5) -> bool:
    """
    Acquire exclusive lock on index file.
    
    Teaching message if lock held by another process (adversarial design).
    
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

**Why:**
- **Prevent:** Index corruption from concurrent writes
- **Teach:** Show correct usage patterns when misuse attempted
- **Simpler:** Avoids blue-green deployment complexity

---

### Pattern 5: Hybrid Search (LanceDB Native)

**File:** `.praxis-os/mcp_server/server/indexes/standards_index.py`

```python
# COPIED from design document
# indexes/standards_index.py

import lancedb
from sentence_transformers import SentenceTransformer

class StandardsIndex(BaseIndex):
    """Hybrid search using LanceDB's native capabilities."""
    
    def __init__(self, cache_path: Path, config: dict):
        # Single LanceDB connection for all indexes!
        self.db = lancedb.connect(str(cache_path / "standards"))
        self.table = self.db.open_table("standards")
        
        # All indexes are LanceDB-native:
        # - Vector index (already exists from table creation)
        # - FTS index (BM25-based, created via create_fts_index)
        # - Scalar indexes (BTREE/BITMAP, created via create_scalar_index)
    
    def build(self, source_paths: List[str], force: bool = False):
        """Build all indexes in LanceDB."""
        # 1. Create/update vector index (default)
        # 2. Create FTS index for keyword search
        self.table.create_fts_index("content")
        
        # 3. Create scalar indexes for metadata filtering
        self.table.create_scalar_index("domain")  # BTREE (high cardinality)
        self.table.create_scalar_index("phase", index_type="bitmap")  # Low cardinality
        self.table.create_scalar_index("role", index_type="bitmap")
    
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        # Build WHERE clause from filters (LanceDB SQL syntax)
        where_clause = self._build_where_clause(filters) if filters else None
        
        # 1. Vector search with prefilter (if filters exist)
        vector_results = (
            self.table.search(query_vector)
            .where(where_clause, prefilter=True)  # Uses scalar indexes!
            .limit(20)
            .to_list()
        )
        
        # 2. FTS (BM25) search with same filter
        fts_results = (
            self.table.search()
            .where(f"content MATCH '{query}' AND {where_clause}", fts=True)
            .limit(20)
            .to_list()
        )
        
        # 3. Reciprocal Rank Fusion (combine both result sets)
        fused = self.reciprocal_rank_fusion(vector_results, fts_results)
        
        # 4. Re-rank top results with cross-encoder
        reranked = self.rerank(query, fused[:10])
        
        return reranked[:n]
```

**Key Simplification:** LanceDB provides vector, FTS (BM25), and scalar indexes natively. **No external rank-bm25 or SQLite needed!**

---

### Pattern 6: Metadata Filtering (Scalar Indexes)

```python
def _build_where_clause(self, filters: dict) -> str:
    """
    Convert filters dict to LanceDB SQL WHERE clause.
    
    Examples:
        {"domain": "backend"} -> "metadata.domain = 'backend'"
        {"domain": ["backend", "frontend"]} -> "metadata.domain IN ('backend', 'frontend')"
        {"domain": "backend", "phase": 0} -> "metadata.domain = 'backend' AND metadata.phase = 0"
    """
    if not filters:
        return None
    
    clauses = []
    
    for key, value in filters.items():
        if isinstance(value, list):
            # Multiple values (OR)
            values_str = ", ".join(f"'{v}'" if isinstance(v, str) else str(v) for v in value)
            clauses.append(f"metadata.{key} IN ({values_str})")
        else:
            # Single value
            value_str = f"'{value}'" if isinstance(value, str) else str(value)
            clauses.append(f"metadata.{key} = {value_str}")
    
    return " AND ".join(clauses)
```

**Why:** Pre-filtering with scalar indexes reduces search space dramatically (60 → 10 docs), improving both speed and accuracy.

---

### Pattern 7: Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(self, list1: List, list2: List, k: int = 60) -> List:
    """
    RRF formula: score = sum(1 / (k + rank_i))
    
    Merges two ranked lists, giving credit to items appearing in both.
    
    Args:
        list1: First ranked list (e.g., vector search results)
        list2: Second ranked list (e.g., FTS results)
        k: Constant for RRF (default 60, standard value)
    
    Returns:
        Merged list sorted by RRF score descending
    """
    scores = {}
    
    # Score items from list 1
    for rank, item in enumerate(list1, start=1):
        item_id = item["chunk_id"]
        scores[item_id] = scores.get(item_id, 0) + (1 / (k + rank))
    
    # Score items from list 2
    for rank, item in enumerate(list2, start=1):
        item_id = item["chunk_id"]
        scores[item_id] = scores.get(item_id, 0) + (1 / (k + rank))
    
    # Sort by RRF score descending
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return items in order
    return [self._get_item_by_id(item_id) for item_id, score in sorted_items]
```

**Why:** RRF is proven effective for combining heterogeneous ranked lists (vector + keyword). k=60 is the standard value from research.

---

### Pattern 8: Re-ranking (Cross-Encoder)

```python
def rerank(self, query: str, results: List[SearchResult], top_n: int = 10) -> List[SearchResult]:
    """
    Re-rank top results using cross-encoder for final ordering.
    
    Only re-rank top N to save compute (cross-encoders are expensive).
    """
    from sentence_transformers import CrossEncoder
    
    # Only re-rank if enabled in config
    if not self.config["retrieval"]["rerank"]["enabled"]:
        return results
    
    # Load cross-encoder model
    model = CrossEncoder(self.config["retrieval"]["rerank"]["model"])
    
    # Create (query, document) pairs
    pairs = [(query, r.content) for r in results[:top_n]]
    
    # Score all pairs
    scores = model.predict(pairs)
    
    # Sort results by new scores
    scored_results = list(zip(results[:top_n], scores))
    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    # Return re-ranked results + remaining unranked results
    return [r for r, score in scored_results] + results[top_n:]
```

**Why:** Re-ranking improves final result quality by 10-15%, but only needed for top N results (expensive operation).

---

## 4. Testing Strategy

### Systematic Approach (from test-generation-js-ts workflow)

**Phase 1: Code Inventory (15 minutes)**
- Read all new/modified files
- Inventory: classes, methods, parameters, return types
- Document complexity: async, try/catch, dependencies

**Phase 2: Dependency Analysis (15 minutes)**
- External dependencies: `lancedb`, `sentence-transformers`, `tree-sitter`, `watchdog`
- Internal dependencies: `rag_engine`, config modules
- **Mocking strategy:**
  - Mock LanceDB tables (avoid actual database in tests)
  - Mock SentenceTransformer model (avoid model download in tests)
  - Mock Tree-sitter parsers (test dynamic loading without actual parsers)

**Phase 3: Test Plan (15 minutes)**
- **Unit tests** (≥80% coverage target, BLOCKING):
  - `BaseIndex` abstract methods
  - `IndexManager.__init__`, `._init_indexes`, `.search`, `._load_config`
  - `StandardsIndex.search`, `._reciprocal_rank_fusion`, `._build_where_clause`
  - `CodeIndex.search`, `._chunk_code`
  - `ASTIndex._load_parsers`, `._parse_file`, `.search`
  - File watcher pattern matching, debouncing
  
- **Integration tests** (≥60% coverage target):
  - End-to-end hybrid search accuracy (measure against test corpus)
  - Metadata filtering effectiveness (verify reduced search space)
  - Code semantic search accuracy
  - AST structural search precision
  - MCP tool integration (`pos_search` end-to-end)

**Phase 4: Test Generation (30 minutes)**
- Generate unit tests for all components
- Test success cases and error cases
- Test graceful degradation (parser unavailable, FTS disabled)

**Phase 5: Quality Validation (10 minutes)**
- Run: `pytest tests/ --cov=server.indexes --cov-report=term-missing --cov-fail-under=80`
- Run: `pylint server/indexes/ --fail-under=10.0`
- Run: `mypy server/indexes/ --strict`

---

## 5. Deployment Guidance

### MCP Integration

**Step 1: Create pos_search Tool**

```python
# server/tools/pos_search.py

@server.tool()
async def pos_search(
    content_type: str,          # "standards", "code", "ast"
    query: str,
    filters: dict = None,       # {"domain": ["iteration"]}
    n_results: int = 5
) -> dict:
    """
    Unified search across all indexed content.
    
    Args:
        content_type: What to search ("standards", "code", "ast")
        query: Natural language query
        filters: Optional metadata filters
        n_results: Number of results
    """
    results = rag_engine.index_manager.search(
        query=query,
        content_types=[content_type],  # Single source (explicit)
        filters=filters,
        n_results=n_results
    )
    
    return format_results(results)
```

**Step 2: Backward Compatibility**

```python
# Existing search_standards delegates to pos_search
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

### Rollback Plan

If issues arise during deployment:

1. **Immediate Rollback:** Keep old RAGEngine as fallback, disable IndexManager via config
2. **Partial Rollback:** Disable specific features (code search, metadata filtering) via config
3. **Debug Mode:** Enable detailed logging, measure performance at each step
4. **Graceful Degradation:** System falls back to vector-only search if FTS/re-ranking fails

---

## 6. Troubleshooting

### Issue 1: "Tree-sitter parser not installed" warnings

**Symptom:** Log warnings during AST index build for certain languages

**Cause:** Tree-sitter parser package not installed for that language

**Solution:**
```bash
# Check config languages
cat .praxis-os/config/index_config.yaml | grep languages

# Install missing parsers
pip install tree-sitter-python tree-sitter-typescript tree-sitter-go
```

**Prevention:** LLM-driven installation (Phase 7) auto-installs detected languages

---

### Issue 2: Hybrid search accuracy not improving

**Symptom:** Hybrid search accuracy same as vector-only

**Cause:** FTS index not built or not being used

**Solution:**
```python
# Verify FTS index exists
assert table.has_fts_index("content")

# Check FTS query is executing
logger.debug(f"FTS query: {fts_query}")

# Measure FTS vs vector results separately
print(f"Vector results: {len(vector_results)}")
print(f"FTS results: {len(fts_results)}")
```

**Prevention:** Validation gate in Phase 2 checks FTS index creation

---

### Issue 3: Index lock acquisition fails

**Symptom:** `BlockingIOError` when running manual index rebuild

**Cause:** MCP server is running and holds the lock

**Solution:**
```bash
# Stop MCP server
kill $(cat .praxis-os/mcp_server.pid)

# Or use MCP tool (preferred)
pos_rebuild_index()  # Handles locking correctly
```

**Prevention:** Teaching message displayed when lock acquisition fails (see Pattern 4)

---

### Issue 4: Query latency >200ms

**Symptom:** Slow search queries, p95 latency >200ms

**Cause:** Large corpus, no pre-filtering, re-ranking all results

**Solution:**
```python
# Enable metadata pre-filtering (reduces search space)
filters = {"domain": "backend"}  # Search only backend standards

# Limit re-ranking to top N (not all results)
rerank_top_n = 10  # Only re-rank top 10, not all 20

# Measure bottlenecks
with Timer("vector_search"):
    vector_results = table.search(...)
with Timer("fts_search"):
    fts_results = table.search(...)
with Timer("rerank"):
    reranked = rerank(...)
```

**Prevention:** Performance validation in Phase 8 measures latency at each step

---

### Issue 5: Test coverage <80%

**Symptom:** `pytest --cov-fail-under=80` fails

**Cause:** Untested error paths, untested private methods

**Solution:**
```python
# Test error cases explicitly
def test_search_unknown_content_type():
    with pytest.raises(ValueError, match="Unknown content_type"):
        index_manager.search(query="test", content_type="invalid")

# Test private methods if complex logic
def test_build_where_clause_multiple_values():
    clause = standards_index._build_where_clause({"domain": ["backend", "frontend"]})
    assert "IN" in clause

# Use coverage report to find gaps
pytest --cov=indexes --cov-report=term-missing
# Look for lines marked MISSING
```

**Prevention:** Systematic test generation (Phase 8, Task 8.5-8.6) targets 80%+ coverage

---

## 7. Key Success Metrics

### Functional Metrics
- [ ] All 12 functional requirements (FR-001 to FR-012) implemented
- [ ] Hybrid search accuracy: 50-60% (baseline 33%)
- [ ] Filtered search accuracy: 70%+ (baseline 50%)
- [ ] Code search functional for detected languages
- [ ] Tree-sitter support for 50+ languages (config-driven)

### Performance Metrics
- [ ] Standards hybrid search latency: <200ms p95
- [ ] Code semantic search latency: <200ms p95
- [ ] AST structural search latency: <100ms p95
- [ ] Metadata filter overhead: <10ms
- [ ] Storage: <1.5GB total
- [ ] Memory: <1GB active

### Quality Metrics (BLOCKING)
- [ ] Unit test coverage: ≥80%
- [ ] Integration test coverage: ≥60%
- [ ] Pylint score: 10.0/10
- [ ] MyPy: 0 errors (strict mode)
- [ ] All existing tests still passing (zero breaking changes)

### Deployment Metrics
- [ ] Installation auto-detects languages (95%+ accuracy)
- [ ] Zero manual config steps required
- [ ] File locking prevents corruption (zero corrupt index events)
- [ ] Graceful degradation tested (system continues with warnings)

---

## 8. Implementation Checklist

Before marking implementation complete:

**Foundation:**
- [ ] BaseIndex abstract class created
- [ ] IndexManager orchestration working
- [ ] StandardsIndex refactored from RAGEngine
- [ ] Backward compatibility verified (search_standards works)

**Hybrid Search:**
- [ ] LanceDB FTS index created
- [ ] Vector + FTS queries executing
- [ ] RRF fusion implemented (k=60)
- [ ] Accuracy improvement measured (33% → 50-60%)

**Metadata Filtering:**
- [ ] Scalar indexes created (BTREE for domain, BITMAP for phase/role)
- [ ] WHERE clause builder working
- [ ] Pre-filtering integrated with vector and FTS
- [ ] Accuracy improvement measured (50% → 70%+)

**Code Search:**
- [ ] CodeIndex semantic search working (BGE embeddings)
- [ ] ASTIndex structural search working (Tree-sitter)
- [ ] Dynamic parser loading with graceful degradation
- [ ] File watcher for incremental updates

**Integration:**
- [ ] pos_search MCP tool created
- [ ] All content types (standards, code, ast) accessible
- [ ] Systematic testing complete (80%+ unit, 60%+ integration)
- [ ] Performance targets met (<200ms latency)
- [ ] Quality gates passed (Pylint 10.0, MyPy 0 errors)

**Deployment:**
- [ ] Installation integration tested end-to-end
- [ ] Documentation updated
- [ ] Rollback plan documented
- [ ] Monitoring/logging in place

---

---

## 9. Complete Configuration Template

**CRITICAL:** This is the FULL `index_config.yaml` copied from the design document. Use this exact structure:

```yaml
# COPIED from design document - DO NOT MODIFY WITHOUT CONSULTING DESIGN DOC

# .praxis-os/config/index_config.yaml

# ============================================================================
# RAG Search Configuration
# ============================================================================
# This file controls how prAxIs OS searches your project's standards and code.
# You don't need to understand the internals - just enable what you want.
#
# TL;DR:
# - vector: Finds by MEANING ("edit files" matches "modify source")
# - fts: Finds by EXACT WORDS ("MCP server" only matches those words) - LanceDB native!
# - metadata: Filters by topic before searching (faster, more accurate) - LanceDB scalar indexes!
# - code: Searches your actual source code (verify docs vs reality)
#
# All features are FREE (zero API cost, runs locally)
# All search features are LanceDB native - no external libraries!

# ============================================================================
# Why Both Vector AND Keyword Search? (Hybrid Search)
# ============================================================================
# Each search method catches different things. Together = better results.
#
# Vector Search (Semantic) is good at:
#   Query: "where do I edit source files during development?"
#   Finds: "file modification locations", "local iteration workflow"
#   → Matches by MEANING, even if words are different
#
# FTS / Keyword Search (BM25-based, LanceDB native!) is good at:
#   Query: "MCP server startup"
#   Finds: Docs with EXACT phrase "MCP server" (not "service" or "daemon")
#   → Matches EXACT TERMS you know you're looking for
#
# Real Example - Why You Need Both:
#   Query: "How does the MCP lifecycle work during dogfooding?"
#
#   Vector ONLY would find:
#   - "service startup process in development" ✓ (meaning is close)
#   - "iteration workflow with running servers" ✓ (semantically similar)
#   - MISSES: Docs that say "MCP" but use different phrasing ✗
#
#   Keyword ONLY would find:
#   - Any doc with "MCP" AND "lifecycle" AND "dogfooding" ✓ (exact match)
#   - MISSES: "server restart during local development" ✗ (no exact keywords)
#
#   HYBRID finds both sets, merges them, you get complete answer!
#
# Bottom line: Vector catches concepts, keyword catches terminology.
#              Hybrid = best of both worlds.

indexes:
  # ---------------------------------------------------------------------------
  # Vector Search (Semantic/Meaning-Based)
  # ---------------------------------------------------------------------------
  # Finds documents by MEANING, not exact words.
  # Example: "where to edit files" matches "file modification locations"
  #
  # How it works: AI model converts text to numbers (embeddings), finds 
  #               similar patterns. Like "search by concept" instead of 
  #               "search by exact phrase."
  #
  # Cost: Zero (runs locally on your machine, no API calls)
  # Speed: ~50-100ms per query
  # Storage: ~134MB model download (one-time)
  
  vector:
    enabled: true
    
    # Which AI model to use for understanding meaning
    # Think of this like choosing search engine quality vs speed:
    #
    # - BAAI/bge-small-en-v1.5: DEFAULT - Good balance (134MB, fast)
    # - BAAI/bge-base-en-v1.5: Better accuracy, slower (438MB, medium)
    # - BAAI/bge-large-en-v1.5: Best accuracy, needs good CPU/GPU (1.3GB, slow)
    # - sentence-transformers/all-MiniLM-L6-v2: Legacy, smaller but less accurate
    #
    # RECOMMENDATION: Start with default, upgrade if you need better accuracy
    model: BAAI/bge-small-en-v1.5  # MIT licensed, zero cost
    
    source_paths:
      - standards/  # All your standards (universal + project)
    
    file_patterns:
      - "*.md"  # Only index markdown files
    
    # -----------
    # Chunking Strategy (How Documents Are Split)
    # -----------
    # Documents are split into smaller pieces for better search accuracy.
    # Think of it like: "Search one paragraph at a time, not entire books."
    #
    # Why chunk? A 5000-word doc might be about 10 topics. If you search for
    # "workflow gates", you want JUST that section, not the whole doc.
    #
    # chunk_size: How many tokens (words) per chunk
    # - Too small (100): Loses context, "What workflow?" (no surrounding info)
    # - Too large (2000): Loses precision, returns entire doc instead of section
    # - Just right (500): ~2-3 paragraphs, enough context + precision
    #
    # chunk_overlap: How many tokens to repeat between chunks
    # - Purpose: Prevents splitting concepts mid-sentence
    # - Example: "...end of chunk 1. Important concept starts here..." 
    #            Without overlap, "Important concept" might be split between chunks
    # - 50 tokens = ~1-2 sentences of overlap
    #
    # When to tune:
    # - Standards are very short (100-200 words)? → Reduce chunk_size to 200
    # - Standards are very long (5000+ words)? → Increase chunk_size to 800
    # - Getting partial answers? → Increase overlap to 100
    # - Default works for 95% of cases!
    
    chunk_size: 500      # ~500 tokens per chunk (2-3 paragraphs) - RECOMMENDED
    chunk_overlap: 50    # Overlap to prevent concept splitting - RECOMMENDED

  # ---------------------------------------------------------------------------
  # Full-Text Search / Keyword Search (Exact Word Matching)
  # ---------------------------------------------------------------------------
  # Finds documents by EXACT WORDS in your query.
  # Example: "MCP server" only matches docs containing those specific words
  #
  # Uses LanceDB's native FTS, which is BM25-based: A smart word-counting 
  # algorithm that:
  # - Counts how often your query words appear
  # - Gives higher scores to rare words (e.g., "MCP" vs "the")
  # - Accounts for document length
  #
  # How it works: LanceDB builds an inverted index (word → documents)
  # Cost: Zero (built into LanceDB, no external library)
  # Speed: ~10-20ms per query (faster than vector search)
  # Storage: ~10MB FTS index
  # 
  # WHY ENABLE THIS: Sometimes you know the exact term you're looking for.
  # Keyword search catches exact matches that semantic search might miss.
  # Together (hybrid search) = best of both worlds.
  #
  # IMPORTANT: This is LanceDB's native FTS (create_fts_index), NOT an external
  # rank-bm25 library. No additional dependencies needed!
  
  fts:
    enabled: true
    source_paths: [standards/]
    
    # FTS Configuration (LanceDB options)
    # See: https://lancedb.com/docs/indexing/fts-index/
    with_position: false      # Phrase queries disabled (faster, smaller index)
    stem: true                # "running" → "run" (better recall)
    remove_stop_words: true   # Remove "the", "a", "is" (better precision)
    ascii_folding: true       # "café" → "cafe" (international text)
    max_token_length: 40      # Filter out base64, long URLs

  # ---------------------------------------------------------------------------
  # Metadata Filtering (Reduce Search Space by Topic)
  # ---------------------------------------------------------------------------
  # Lets you filter by topic/domain BEFORE searching.
  # Example: pos_search(query="...", filters={"domain": ["workflow"]})
  #          → Only searches workflow-related standards
  #
  # How it works: 
  # 1. Metadata fields (domain, phase, role) are stored as columns in LanceDB
  # 2. Scalar indexes (BTREE/BITMAP) built on these columns
  # 3. SQL WHERE clauses filter BEFORE search: "domain = 'workflow'"
  # 4. LanceDB uses indexes for fast filtering (sub-ms even at billions of records)
  #
  # Index Types:
  # - BTREE: For high-cardinality fields (domain, audience) - many unique values
  # - BITMAP: For low-cardinality fields (phase, role) - few unique values (<1000)
  #
  # Cost: Zero (LanceDB native, no external database)
  # Speed: Sub-millisecond filtering via indexed WHERE clauses
  # Storage: ~1-5MB scalar indexes (depends on cardinality)
  #
  # WHY ENABLE THIS: 
  # - At 60 standards: Nice to have (faster queries)
  # - At 200 standards: Very helpful (much faster, more accurate)
  # - At 500 standards: CRITICAL (search would be too slow/inaccurate without it)
  #
  # This is what keeps prAxIs OS working at scale!
  #
  # IMPORTANT: This uses LanceDB's scalar indexes (create_scalar_index), NOT SQLite!
  # No additional database needed!
  
  metadata:
    enabled: true
    
    # Scalar indexes to create (LanceDB native)
    scalar_indexes:
      - column: domain
        index_type: btree    # High cardinality (many unique domains)
      - column: phase
        index_type: bitmap   # Low cardinality (8 phases: 1-8)
      - column: role
        index_type: bitmap   # Low cardinality (few roles: agent, human, framework)
      - column: audience
        index_type: btree    # Medium-high cardinality
    
    # How to generate metadata for your standards
    # - auto_generate: Extract from headers/keywords (zero cost, good enough)
    # - llm_enhance: Use LLM to generate better metadata (costs ~$0.01/doc one-time)
    auto_generate: true
    llm_enhance: false  # Optional: Better metadata, costs money

  # ---------------------------------------------------------------------------
  # Code Search (Search Your Project's Source Code)
  # ---------------------------------------------------------------------------
  # Find functions, classes, implementations in your actual codebase.
  # Example: pos_search(content_type="code", query="how does StateManager work")
  #          → Returns actual code locations, not just docs
  #
  # How it works: 
  # - Parses code structure (AST - Abstract Syntax Tree)
  # - Extracts function/class names (symbols)
  # - Creates semantic embeddings of code
  #
  # Cost: Zero (local parsing + embeddings)
  # Speed: ~100ms per query
  # Storage: ~200MB for 100K lines of code
  #
  # WHY ENABLE THIS:
  # - Verify docs against actual implementation (trust but verify)
  # - Find where features are actually implemented
  # - Understand how code works without reading everything
  #
  # NEW BEHAVIORAL PATTERN: AI can check if docs match reality!
  
  code:
    enabled: false  # Enable when you're ready to index your code
    
    source_paths:
      - ../src   # Relative to .praxis-os/ directory
      - ../lib
    
    # Which programming languages to index
    # Supported: python, javascript, typescript, go, rust, java, csharp
    # Add more as needed - it's config-driven!
    languages:
      - python
      - javascript
      - typescript
    
    file_patterns:
      - "*.py"
      - "*.js"
      - "*.ts"
      - "*.jsx"
      - "*.tsx"
    
    # What to exclude from indexing
    exclude_patterns:
      - "*/node_modules/*"   # Don't index dependencies
      - "*/__pycache__/*"    # Don't index Python cache
      - "*/venv/*"           # Don't index virtual env
      - "*/dist/*"           # Don't index build output
      - "*/build/*"
    
    index_tests: false  # Usually don't need to search test files

# ============================================================================
# Search Strategy Configuration
# ============================================================================
# How different search methods are combined for best results

retrieval:
  # ---------------------------------------------------------------------------
  # Hybrid Search (Combine FTS + Vector)
  # ---------------------------------------------------------------------------
  # Combines FTS (Full-Text Search / keyword) + Vector (semantic) results.
  #
  # Why: FTS finds exact matches, semantic search finds similar meaning. 
  #      Together you catch both "MCP server" (exact) and 
  #      "service implementation" (similar meaning).
  #
  # How it works:
  # 1. Run vector search → Top 20 results
  # 2. Run FTS search → Top 20 results  
  # 3. Merge using Reciprocal Rank Fusion (RRF)
  # 4. Re-rank top 10 with cross-encoder
  # 5. Return top N
  #
  # Algorithm: Reciprocal Rank Fusion (RRF)
  # - Standard algorithm for merging search results
  # - Works well, no tuning needed
  # - Alternative: "weighted" (custom weights, rarely needed)
  #
  # IMPORTANT: Both vector and FTS happen in single LanceDB instance!
  
  fusion_strategy: reciprocal_rank  # How to merge FTS + vector results
  
  # ---------------------------------------------------------------------------
  # Re-Ranking (Improve Top Results)
  # ---------------------------------------------------------------------------
  # After initial search, re-score top 10 results with a more accurate model.
  #
  # How it works: 
  # 1. Initial search returns top 20 candidates (fast but rough)
  # 2. Re-ranker scores top 10 more carefully (slower but accurate)
  # 3. Return best 5 to you
  #
  # Cost: Zero (local cross-encoder model)
  # Speed: +20ms per query (worth it for better accuracy)
  # Storage: +50MB model
  #
  # RESULT: Better results at rank 1, fewer "almost right" answers
  
  rerank:
    enabled: true
    model: cross-encoder/ms-marco-MiniLM-L-12-v2  # MIT licensed, zero cost

# ============================================================================
# Monitoring & File Watching
# ============================================================================

monitoring:
  track_query_performance: true  # Log query times for optimization
  log_level: INFO  # DEBUG, INFO, WARNING, ERROR
  
  # ---------------------------------------------------------------------------
  # File Watcher (Hot Reload for Standards & Code)
  # ---------------------------------------------------------------------------
  # Automatically rebuilds indexes when files change during development.
  #
  # How it works:
  # 1. Watchdog monitors configured paths for file changes
  # 2. Debouncing prevents rebuild thrashing (waits N seconds after last change)
  # 3. Incremental rebuild updates only changed files
  # 4. RAG engine reloads with fresh index (query results immediately current)
  #
  # Why different debounce times:
  # - Standards: Change infrequently (new docs), 5 seconds is responsive
  # - Code: Changes constantly (every file save), 10 seconds prevents thrashing
  #
  # IMPORTANT: Exclude patterns prevent indexing dependencies, build artifacts!
  
  file_watcher:
    enabled: true  # Enable automatic index updates
    
    watched_content:
      # Standards watching (documentation)
      standards:
        paths: [standards/]  # Relative to .praxis-os/
        patterns: ["*.md", "*.json"]  # Markdown standards + workflow metadata
        exclude: []  # No excludes needed (all standards are relevant)
        debounce_seconds: 5  # Quick response for doc changes
      
      # Code watching (your project source)
      # IMPORTANT: Patterns auto-detected during install based on project languages
      code:
        enabled: true  # Can disable code watching per project
        paths: [../src, ../lib, ../app]  # Relative to .praxis-os/, adjust for your project
        
        # File patterns (auto-generated during install, edit to add languages)
        # To add a new language: Just add its extension pattern!
        patterns:
          - "*.py"      # Python
          - "*.js"      # JavaScript
          - "*.jsx"     # React
          - "*.ts"      # TypeScript
          - "*.tsx"     # React TypeScript
          # - "*.go"    # Uncomment to add Go
          # - "*.rs"    # Uncomment to add Rust
          # - "*.java"  # Uncomment to add Java
        exclude:
          # Dependency directories (don't index third-party code)
          - "**/node_modules/**"
          - "**/venv/**"
          - "**/.venv/**"
          
          # Build artifacts (generated code, not source)
          - "**/dist/**"
          - "**/build/**"
          - "**/__pycache__/**"
          - "**/*.pyc"
          
          # Version control
          - "**/.git/**"
          
          # Test coverage reports
          - "**/htmlcov/**"
          - "**/coverage/**"
        
        debounce_seconds: 10  # Longer debounce for frequently-changing code
        
        # Optional: Only watch specific subdirectories for large projects
        # paths: [../src/core, ../src/api]  # Narrow scope for faster rebuilds
```

---

**End of Implementation Guidance**

For detailed task breakdown, see `tasks.md`.  
For technical specifications, see `specs.md`.  
For requirements, see `srd.md`.

