# Multi-Index RAG Architecture - Design Document

**Date:** 2025-11-01  
**Author:** Claude + Josh (paired)  
**Status:** Design Review (UPDATED after LanceDB research)  
**Timeline:** Single day implementation (14-18 hours with code search + tree-sitter + watcher)

---

## ⚡ Architecture Simplification (Post-Research Update)

**Original Design:** 3 databases (LanceDB + rank-bm25 + SQLite)
- LanceDB for vector search
- rank-bm25 library for keyword search
- SQLite for metadata filtering

**Research Discovery:** LanceDB has **ALL capabilities built-in!**
- ✅ Vector search (native)
- ✅ Full-Text Search (BM25-based, native!)
- ✅ Scalar indexes (BTREE/BITMAP for metadata, native!)

**Updated Design:** **Single database (LanceDB only)**
- Simpler architecture
- Better performance (sub-100ms at billions of records)
- Fewer dependencies
- Easier maintenance

**This is why external research matters!** Initial design was based on assumptions. Actual documentation revealed much simpler path.

---

## 🎯 Executive Summary

**Problem:** RAG discovery will degrade from 33% → 5% accuracy as standards corpus grows to 500+, breaking the behavioral modification system that makes prAxIs OS work.

**Solution:** Multi-index, config-driven RAG architecture supporting:
1. **Hybrid Search** (FTS + Vector) - LanceDB's native FTS (BM25-based) for keywords + vector for semantics
2. **Metadata Filtering** - LanceDB's scalar indexes (BTREE/BITMAP) with SQL WHERE clauses
3. **Code Search - Semantic** - BGE embeddings on code text (same model as standards)
4. **Code Search - Structure** - Tree-sitter AST queries, **all 50+ languages supported day 1** (config-driven, dynamic imports)
5. **Unified Tool** (`pos_search`) - Single tool, explicit content_type selection
6. **LLM-Driven Install** - AI agent detects languages, generates config, installs dependencies
7. **Index Safety** - File locking prevents corruption (adversarial design: prevent + teach)

**Constraint:** Zero-cost (open source, local models only), completes TODAY.

**Impact:** 
- Preserves behavioral system at scale (500+ standards)
- Enables code verification ("trust but verify" against docs)
- **Critical for AI-generated codebases** (32K lines in 2.5 months = need fast discovery)

---

## 📊 Problem Statement

### Current State (60 Standards)

**RAG Architecture:**
- Single vector index (LanceDB)
- Single content type (markdown standards)
- Single retrieval strategy (semantic search)
- Single tool (`search_standards`)

**Discovery Performance:**
- Single-query accuracy: 33%
- Multi-query success: 90% (within 3 queries)
- **Status:** Acceptable, behavioral system works

### Projected State (500 Standards)

**Semantic Overlap Increases:**
- 10-15 standards now share "development", "workflow", "testing"
- At 500 standards: 50+ standards share common terms
- Math: `Accuracy ≈ 1 / (Overlap Factor)` → 33% → 5%

**Behavioral System Breaks:**
```
Current (33% accuracy):
Query 1: Miss
Query 2: Miss  
Query 3: Hit ✓
→ Multi-query pattern TRAINS better behavior ✓

Projected (5% accuracy):
Query 1-9: Miss
Query 10: Give up, guess instead
→ Behavioral system COLLAPSES ❌
```

**Critical Insight:** Discovery degradation doesn't just slow me down—it **undermines the adversarial design** that makes prAxIs OS work. If querying is too expensive, I revert to training data.

### Why This Matters Now

**prAxIs OS gaining traction:**
- Young project, but growing interest
- Per-project installations (single-tenant)
- Goal: AI becomes project-specific expert

**Growth Scenarios:**
- Small project: 60 universal + 10 project = 70 standards
- Medium enterprise: 150 universal + 50 project = 200 standards  
- Large enterprise: 200 universal + 300 project = 500 standards

**Without intervention:** System breaks at 200-300 standards (6-12 months from now)

**With proactive architecture:** Scales confidently to 500+ standards

---

## 🎯 Goals & Non-Goals

### In Scope (This Design)

1. ✅ **Multi-Index Architecture**
   - Foundation supporting multiple content types
   - Config-driven (no code changes for new indexes)
   - Extensible abstractions

2. ✅ **Hybrid Search (FTS + Vector)**
   - LanceDB's native FTS (BM25-based) for keyword precision
   - Vector search for semantic understanding
   - Reciprocal Rank Fusion
   - Improves accuracy: 33% → 50-60%

3. ✅ **Metadata Filtering**
   - LanceDB's scalar indexes (BTREE/BITMAP)
   - Domain/role/audience filters via SQL WHERE clauses
   - Reduces search space dramatically
   - Improves accuracy: 50% → 70%+ (with filters)

4. ✅ **Code Search**
   - AST parsing + symbol extraction
   - Search project source code
   - NEW behavioral dimension: "Trust but verify"

5. ✅ **Unified Tool (`pos_search`)**
   - Single tool, explicit content_type
   - Replaces `search_standards`
   - Clean cutover (no deprecation)

6. ✅ **Zero-Cost Constraint**
   - Local models only (sentence-transformers, cross-encoder)
   - No API costs beyond LLM
   - Open source, Apache 2.0 licensed

### Out of Scope (Future Work)

- ❌ **Dependencies Index** - Phase 6 (curated library docs)
- ❌ **Cross-Index Search** - Query multiple types at once
- ❌ **Query Expansion** - LLM-based (violates zero-cost) or classical NLP (defer)
- ❌ **Windows Support** - Unix-only for now (fcntl locking)

### Success Criteria

**Behavioral System Preserved:**
- Multi-query pattern still works at 500 standards
- Discovery doesn't degrade catastrophically
- AI continues querying (doesn't give up and guess)

**Capabilities Extended:**
- Can search project code (not just docs)
- Can verify docs against implementation
- New behavioral pattern: code verification

**Architecture Quality:**
- Config-driven (add indexes by editing YAML)
- Zero breaking changes to existing functionality
- Completes in single day (12-16 hours)

---

## 🏗️ Proposed Solution

### High-Level Architecture

```
User Query
    ↓
pos_search(content_type="standards", query="...", filters={})
    ↓
IndexManager (orchestration)
    ↓
├─ content_type="standards" → StandardsIndex
│   ├─ LanceDB Vector Index (semantic search)
│   ├─ LanceDB FTS Index (BM25 keyword search - NATIVE!)
│   └─ LanceDB Scalar Indexes (BTREE/BITMAP for metadata - NATIVE!)
│       ↓
│   Hybrid Fusion (RRF) - combines vector + FTS results
│       ↓
│   Re-rank (cross-encoder)
│       ↓
│   Return SearchResult[]
│
├─ content_type="code" → CodeIndex
│   ├─ ASTIndex (Python/JS/TS)
│   ├─ SymbolIndex (functions/classes)
│   └─ VectorIndex (code embeddings)
│       ↓
│   Weighted Fusion
│       ↓
│   Return SearchResult[]
│
└─ content_type="dependencies" → DependenciesIndex (Phase 6)
```

### Component Design

#### 1. Abstract Base Class

```python
# indexes/base.py

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

#### 2. Index Manager (Orchestration)

```python
# index_manager.py

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

#### 3. Standards Index (Hybrid)

```python
# indexes/standards_index.py

class StandardsIndex(BaseIndex):
    """Hybrid search using LanceDB's native capabilities."""
    
    def __init__(self, cache_path: Path, config: dict):
        import lancedb
        
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

**Why:** Uses LanceDB's native FTS (BM25), scalar indexes (BTREE/BITMAP), and SQL WHERE clauses. **No external libraries needed!** Sub-100ms even at billions of records.

#### 4. Code Index (AST + Symbols)

```python
# indexes/code_index.py

class CodeIndex(BaseIndex):
    """Search project source code: AST + Symbols + Semantic."""
    
    def __init__(self, cache_path: Path, config: dict):
        self.ast_index = ASTIndex()          # Parse AST by language
        self.symbol_index = SymbolIndex()    # Extract functions/classes
        self.vector_index = CodeVectorIndex()  # Code embeddings
        
        # Language configs from YAML
        self.languages = config["languages"]  # ["python", "javascript", "typescript"]
    
    def build(self, source_paths: List[str], force: bool = False):
        """Parse code by language, extract AST + symbols."""
        for lang in self.languages:
            parser = self._get_parser(lang)  # tree-sitter or language-specific
            # Parse, extract symbols, build indexes
    
    def search(self, query: str, filters: dict, n: int) -> List[SearchResult]:
        # 1. Symbol search (exact function/class matches)
        symbol_results = self.symbol_index.search(query, n=10)
        
        # 2. Semantic code search
        vector_results = self.vector_index.search(query, n=10)
        
        # 3. AST pattern matching
        ast_results = self.ast_index.search(query, n=10)
        
        # 4. Weighted fusion (symbols > semantic > AST)
        return self.weighted_fusion(symbol_results, vector_results, ast_results)[:n]
```

**Why:** Different strategies for code vs text. Symbols for exact matches, semantic for concepts, AST for patterns.

#### 5. Configuration (Self-Teaching YAML)

```yaml
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

**Why This Config Design:**
- **Self-teaching**: Explains what each feature does, why you'd want it
- **Beginner-friendly**: No ML jargon without explanation
- **Queryable**: Comments teach same way prAxIs OS does (just-in-time learning)
- **Config-driven**: Enable/disable features by editing YAML, no code changes

#### 6. MCP Tool (pos_search)

```python
# server/tools/rag_tools.py

@server.tool()
async def pos_search(
    content_type: str,          # "standards", "code", "dependencies"
    query: str,
    filters: dict = None,       # {"domain": ["iteration"]}
    n_results: int = 5
) -> dict:
    """
    Unified search across all indexed content.
    
    Args:
        content_type: What to search ("standards", "code", "dependencies")
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

**Why:** Single tool. Explicit content_type. I make cognitive decision about what to search. Clean cutover (replaces `search_standards`).

---

## 🔄 Data Flow Examples

### Example 1: Standards Search (Hybrid + Metadata)

```python
# My query
pos_search(
    content_type="standards",
    query="where to edit MCP server files",
    filters={"domain": ["iteration"]},
    n_results=5
)

# Flow (LanceDB Native!)
1. IndexManager routes to StandardsIndex
2. Build WHERE clause: "domain = 'iteration'"
3. Vector search with prefilter:
   - table.search(query_vector).where("domain = 'iteration'", prefilter=True).limit(20)
   - Uses BTREE scalar index → Fast metadata filtering → 10 docs
4. FTS search with same prefilter:
   - table.search().where("content MATCH 'edit MCP server files' AND domain = 'iteration'", fts=True).limit(20)
   - Uses FTS index + scalar index → Keyword matches on 10 docs
5. Reciprocal Rank Fusion merges vector + FTS scores
6. Cross-encoder re-ranks top 10 results
7. Return top 5

# Result
[
  {content: "...", file: "dogfooding-model.md", score: 0.95},
  {content: "...", file: "mcp-server-update.md", score: 0.82},
  ...
]
```

**Improvement:** Scalar index filtering (60 → 10 docs) + Hybrid search (FTS + vector) = High accuracy

**Key Insight:** Single LanceDB query handles metadata filter + search. No separate SQLite or rank-bm25 library!

### Example 2: Code Search

```python
# My query
pos_search(
    content_type="code",
    query="how does workflow state management work",
    n_results=5
)

# Flow
1. IndexManager routes to CodeIndex
2. SymbolIndex searches for: StateManager, WorkflowEngine classes
3. VectorIndex searches code semantically
4. ASTIndex searches AST patterns
5. Weighted fusion (symbols prioritized)
6. Return top 5 code locations

# Result
[
  {content: "class StateManager:", file: "state_manager.py", lines: (45, 120)},
  {content: "def save_state(...)", file: "state_manager.py", lines: (67, 85)},
  ...
]
```

**New Capability:** Can now find implementation, not just docs. Behavioral extension: verify docs against code.

---

## 🧪 Technology Stack (Zero-Cost, Simplified!)

| Component | Technology | License | Cost |
|-----------|-----------|---------|------|
| **Vector Search** | LanceDB (native) | Apache 2.0 | Zero |
| **Full-Text Search (BM25)** | LanceDB FTS (native!) | Apache 2.0 | Zero |
| **Metadata Filtering** | LanceDB Scalar Indexes (native!) | Apache 2.0 | Zero |
| **Embeddings** | sentence-transformers (BGE) | MIT | Zero |
| **Re-ranking** | cross-encoder | Apache 2.0 | Zero |
| **AST Parsing** | ast (Python), esprima (JS) | Open Source | Zero |
| **Config** | PyYAML | MIT | Zero |

**Key Insight:** LanceDB provides Vector, FTS (BM25), AND metadata filtering natively. **No external rank-bm25 or SQLite needed!**

**Total API Cost:** ZERO beyond LLM calls ✅

**Architecture Simplification:** Originally designed with 3 databases (LanceDB + rank-bm25 + SQLite). Research revealed LanceDB has all capabilities built-in. **Single database, simpler code, better performance.**

### Embedding Model Options (All MIT Licensed, Config-Driven)

| Model | Parameters | Size | Speed | Accuracy | Use Case |
|-------|-----------|------|-------|----------|----------|
| **bge-small-en-v1.5** (default) | 33.4M | 134MB | ~50-100ms | Good | Balanced, recommended |
| **bge-base-en-v1.5** | 109M | 438MB | ~150-200ms | Better | Higher accuracy |
| **bge-large-en-v1.5** | 335M | 1.3GB | ~300ms+ | Best | Max accuracy, GPU |
| **all-MiniLM-L6-v2** | 22M | 90MB | ~30-50ms | Adequate | Legacy/minimal |

**Config-Driven:** Users select via `index_config.yaml`, no code changes needed.

**Default Choice:** `bge-small-en-v1.5` (best balance of accuracy/speed/size)

**Resource Requirements (with bge-small):**
- Storage: ~1.3GB (models + indexes for 500 standards)
- Memory: ~1GB active (all indexes + models loaded)
- Query Latency: <200ms

---

## 🔀 Alternatives Considered

### Alternative 1: API-Based Embeddings (OpenAI, Anthropic)

**Pros:**
- Higher quality embeddings
- No model download

**Cons:**
- ❌ **Violates zero-cost constraint**
- ❌ API dependency
- ❌ Rate limits
- ❌ Privacy concerns (user code/docs sent to API)

**Decision:** REJECTED. Zero-cost is non-negotiable.

### Alternative 2: Multiple Tools (search_standards, search_code, etc.)

**Pros:**
- Separate concerns
- Backward compatible

**Cons:**
- Tool proliferation
- Naming conflicts potential
- Harder to extend

**Decision:** REJECTED. Unified `pos_search` follows established pattern (pos_workflow, pos_browser).

### Alternative 3: Multi-Source Queries (search multiple types at once)

**Pros:**
- Convenience for cross-cutting queries

**Cons:**
- Removes cognitive decision-making (my value-add)
- Less explicit (violates adversarial design)
- Complex result mixing

**Decision:** REJECTED. Single content_type per query. I make intentional decision about what to search.

### Alternative 4: LLM Re-ranking

**Pros:**
- More accurate than cross-encoder

**Cons:**
- ❌ **Violates zero-cost constraint**
- ❌ Adds $0.001 per query (~$10/day @ 10K queries)
- ❌ Slower (500ms vs 20ms)

**Decision:** REJECTED. Cross-encoder is "good enough" and zero-cost.

### Alternative 5: Defer Everything (Wait for Pain)

**Pros:**
- No work now
- See if problem actually happens

**Cons:**
- Math predicts failure at 200-300 standards (6-12 months)
- Migration later is expensive
- Behavioral system breaks = users churn
- Competitors don't have this problem

**Decision:** REJECTED. Proactive architecture now vs expensive fix later.

---

## ⚠️ Risks & Mitigations

### Risk 1: Implementation Takes Longer Than 1 Day

**Probability:** Medium  
**Impact:** Medium (delayed, but not blocked)

**Mitigation:**
- Start with foundation + hybrid (Phase 1-2, 4-6 hours)
- Add metadata + code search incrementally (Phase 3-5, 6-10 hours)
- Worst case: Ship foundation first, add rest next day

**Contingency:** Prioritize hybrid search (biggest accuracy win), defer code search if needed.

### Risk 2: Local Models Insufficient Quality

**Probability:** Low  
**Impact:** Medium (worse accuracy than expected)

**Mitigation:**
- Use proven models (sentence-transformers, cross-encoder widely used)
- Benchmark against current vector-only baseline
- Can swap models via config if needed

**Contingency:** Test with current 60 standards first, validate improvement before full deployment.

### Risk 3: Code Search Too Complex (Language-Specific)

**Probability:** Medium  
**Impact:** Low (can defer to Phase 6)

**Mitigation:**
- Start with Python only (prAxIs OS is Python)
- Use standard library `ast` module (no dependencies)
- JS/TS via esprima/babel (well-established)

**Contingency:** Ship standards indexes first, add code search separately if it takes longer.

### Risk 4: Breaking Changes to Existing Functionality

**Probability:** Low  
**Impact:** Critical (breaks current users)

**Mitigation:**
- Comprehensive testing before deployment
- Keep backward-compatible interfaces
- Clean cutover via MCP tools/list (no deprecation period)

**Contingency:** Rollback plan: revert MCP tool changes, keep old RAGEngine.

### Risk 5: Performance Degradation

**Probability:** Low  
**Impact:** Medium (slower queries)

**Mitigation:**
- Lazy-load indexes (only load when queried)
- Benchmark query latency: target <200ms
- Optimize hot paths (RRF, re-ranking)

**Contingency:** Disable expensive features via config (e.g., re-ranking) if latency unacceptable.

---

## 📝 Implementation Plan

**Total Time:** 14-18 hours (single day with focus, or 2 days comfortably)

### Phase Summary

| Phase | Goal | Time | Key Deliverable |
|-------|------|------|----------------|
| **1. Foundation** | Extensible architecture | 2-3 hours | IndexManager + BaseIndex |
| **2. Hybrid Search** | FTS + Vector fusion | 1.5-2 hours | 33% → 50-60% accuracy |
| **3. Metadata Filtering** | Scalar indexes (BTREE/BITMAP) | 2-2.5 hours | Domain/phase/role filters |
| **4. Code Search - Semantic** | BGE embeddings on code | 1-1.5 hours | Concept-based code discovery |
| **5. Code Search - Structure** | Tree-sitter AST queries | 3-3.5 hours | Precise function/class location |
| **6. File Watcher for Code** | Incremental code index updates | 1-1.5 hours | Hot reload for code changes |
| **7. Installation Integration** | LLM-driven config generation | 1-1.5 hours | Auto-detect languages, install deps |
| **8. Integration & Testing** | pos_search tool + validation | 1-2 hours | End-to-end working system |

**Phases 4-5 (Code Search) Context:**
- 32,000-line AI-generated SDK in 2.5 months validates code search necessity
- grep insufficient for complex codebases with mixins, dynamic inheritance
- Tree-sitter provides structure queries: "Where is X defined?" vs "Where is X mentioned?"

---

### Phase 1: Foundation (2-3 hours)

**Goal:** Extensible architecture, zero breaking changes

**Tasks:**
1. Create `indexes/base.py` (30 min)
   - SearchResult dataclass
   - BaseIndex abstract class

2. Create `index_manager.py` (60 min)
   - IndexManager orchestration
   - Config loading (YAML)
   - Hybrid fusion logic

3. Create `indexes/standards_index.py` (45 min)
   - Move current RAGEngine vector logic
   - Implement BaseIndex interface

4. Update `rag_engine.py` (30 min)
   - Delegate to IndexManager
   - Preserve backward compatibility

5. Create `index_config.yaml` (15 min)

**Validation:** Current `search_standards` still works, no regressions.

### Phase 2: Hybrid Search (1.5-2 hours) - **SIMPLIFIED!**

**Goal:** FTS (BM25) + Vector fusion, 33% → 50-60% accuracy

**Tasks:**
1. Enable LanceDB FTS index in `standards_index.py` (30 min)
   - Add `table.create_fts_index("content")` to build process
   - Configure FTS options (stemming, stop words, etc.)

2. Update search to query both vector + FTS (45 min)
   - Vector search: `table.search(query_vector).limit(20)`
   - FTS search: `table.search().where("content MATCH '...'", fts=True).limit(20)`

3. Implement Reciprocal Rank Fusion in `index_manager.py` (30 min)
   - Merge vector + FTS results by rank

4. Add cross-encoder re-ranking (30 min)
   - Download model (cross-encoder/ms-marco-MiniLM-L-12-v2)
   - Integrate in IndexManager

5. Enable in config, test (15 min)

**Validation:** Query "where to edit MCP server code" returns correct doc with better keyword matching.

**Key Simplification:** No external BM25 library! LanceDB FTS is BM25-based and built-in.

### Phase 3: Metadata Filtering (2-2.5 hours) - **SIMPLIFIED!**

**Goal:** Scalar indexes (BTREE/BITMAP) for metadata filtering, reduce search space

**Tasks:**
1. Add metadata fields to standards table schema (30 min)
   - domain, phase, role, audience fields
   - Ensure all standards have metadata in YAML frontmatter

2. Create scalar indexes in `standards_index.py` (30 min)
   - `table.create_scalar_index("domain")` (BTREE)
   - `table.create_scalar_index("phase", index_type="bitmap")` (BITMAP for low-cardinality)
   - `table.create_scalar_index("role", index_type="bitmap")`

3. Update search to use WHERE clauses for filtering (45 min)
   - Build SQL WHERE clause from filters dict
   - Apply prefilter to both vector and FTS searches
   - Example: `.where("domain = 'workflow' AND phase = 3", prefilter=True)`

4. Add metadata to 60 universal standards (45 min)
   - Script to auto-generate from headers (rule-based)
   - Manual review high-value standards

5. Expose filters in `pos_search` tool (30 min)

6. Update agent guidance to use filters (30 min)

### Phase 4: Code Search - Semantic (1-1.5 hours)

**Goal:** Semantic code search using same BGE model, zero new dependencies

**Tasks:**
1. Create `indexes/code_index.py` (45 min)
   - CodeIndex class implementing BaseIndex
   - Use same embedding model as standards (BGE)
   - Treat code as text (no parsing yet)
   - Store in LanceDB with file path, language metadata

2. Add code indexing to IndexManager (15 min)
   - Route "code" content_type to CodeIndex
   - Handle code file discovery (.py, .js, .ts, etc.)

3. Test semantic code search (15 min)
   - Query: "state management" → finds StateManager class
   - Query: "error handling" → finds try/except patterns
   - Validate results are useful

**Validation:** Can find code by concept, not just filename.

### Phase 5: Code Search - Structure (Tree-sitter) (3-3.5 hours)

**Goal:** AST-based structure queries for precise code search

**✅ Q2/Q3 ANSWER - All Tree-sitter Languages Supported Day 1:**
- **Config-driven, no hardcoded language list**
- **Dynamic imports:** `importlib.import_module(f"tree_sitter_{language}")`
- **Convention-based:** Follows `tree-sitter-{language}` package pattern
- **User-extensible:** User adds language to config + `pip install tree-sitter-{lang}`, no prAxIs OS update needed
- **50+ languages available** (whatever Tree-sitter supports)
- **No frozen mapping file** - relies on ecosystem conventions (see `config-driven-dynamic-logic.md` standard)

**Tasks:**
1. Create `indexes/tree_sitter_index.py` (90 min)
   - ASTIndex class for tree-sitter queries
   - **Dynamic language support:** Discovers parsers at runtime via importlib
   - Query patterns: function definitions, class definitions, imports
   - Store symbols and structure in LanceDB

2. Update CodeIndex for hybrid search (45 min)
   - Combine semantic (BGE) + structure (tree-sitter)
   - Semantic: "what does this do?"
   - Structure: "where is this defined?"

3. Add tree-sitter query library (30 min)
   - Common queries: find_functions, find_classes, find_calls
   - Language-agnostic query interface

4. Test structure queries (30 min)
   - "Where is StateManager defined?" → Exact line
   - "Find all calls to start_span()" → All invocations
   - "What classes use TracerMixin?" → Inheritance chain

**Validation:** Structure queries return precise AST locations.

### Phase 6: File Watcher for Code (1-1.5 hours)

**Goal:** Incremental code index updates as files change during development

**Context:** Current watcher only watches standards (.md/.json), need to add code watching.

**Current Architecture:**
```python
# mcp_server/monitoring/watcher.py
class AgentOSFileWatcher:
    - Watches standards/ for .md and .json
    - Debounces changes (5 seconds)
    - Calls IndexBuilder.build_index(incremental=True)
    - Reloads RAG engine
```

**Proposed Architecture:**
```python
# Purely config-driven watcher
class AgentOSFileWatcher:
    def __init__(self, config_path: Path):
        # Load ALL configuration from YAML
        self.config = self._load_config(config_path / "index_config.yaml")
        self.watched_content = self.config["monitoring"]["file_watcher"]["watched_content"]
        
        # Build pattern matchers from config
        self.matchers = {
            content_type: self._build_matcher(watch_config)
            for content_type, watch_config in self.watched_content.items()
            if watch_config.get("enabled", True)  # Allow disabling per content type
        }
        
        # Per-content-type debouncing state
        self.rebuild_pending = {}  # {content_type: bool}
        self.debounce_timers = {}  # {content_type: float}
    
    def on_modified(self, event):
        # Determine content type from path + pattern (config-driven!)
        content_type = self._match_content_type(event.src_path)
        if content_type:
            self._schedule_rebuild(content_type)
    
    def _match_content_type(self, file_path: str) -> Optional[str]:
        """
        Match file path against configured patterns.
        Returns content_type if matched, None otherwise.
        
        Config-driven: patterns, excludes all from YAML.
        """
        for content_type, matcher in self.matchers.items():
            if matcher.matches(file_path):
                return content_type
        return None
    
    def _schedule_rebuild(self, content_type: str):
        """
        Debounce per content type using configured debounce_seconds.
        
        Config-driven: debounce time from YAML per content type.
        """
        debounce_seconds = self.watched_content[content_type]["debounce_seconds"]
        # ... debounce logic with config-driven timing
        # Call IndexManager.rebuild_index(content_type)
```

**Tasks:**
1. Make watcher purely config-driven (45 min)
   - **Remove all hardcoded file patterns from watcher code**
   - Load `index_config.yaml` on initialization
   - Build pattern matchers from config
   - Per-content-type debouncing from config
   - **Zero hardcoded knowledge of languages**

2. Add pattern matching library (15 min)
   - Use `pathlib.Path.match()` or `fnmatch` for glob patterns
   - Support `**` wildcards (e.g., `**/*.py`)
   - Exclude patterns work like `.gitignore`

3. Integrate with IndexManager (20 min)
   - Change from calling IndexBuilder directly
   - Call `IndexManager.rebuild_index(content_type="code")`
   - IndexManager routes to correct index (CodeIndex, StandardsIndex, etc.)

4. Test config flexibility (20 min)
   - Edit Python file → index updates (from config patterns)
   - Edit JS file → index updates (from config patterns)
   - **Add new language to config (Go) → watcher picks it up automatically**
   - Verify excludes work (node_modules ignored)

**Key Design Principle:**
```python
# BAD: Hardcoded patterns
if file_path.endswith(('.py', '.js', '.ts')):
    rebuild_code_index()

# GOOD: Config-driven
for content_type, config in self.watched_content.items():
    if self._matches_patterns(file_path, config['patterns'], config['exclude']):
        self._schedule_rebuild(content_type)
```

**Config Integration:**
```yaml
# index_config.yaml
monitoring:
  file_watcher:
    enabled: true
    debounce_seconds: 5  # Standards (slow changing)
    
    watched_content:
      standards:
        paths: [standards/]
        patterns: ["*.md", "*.json"]
        exclude: []
        debounce_seconds: 5
      
      code:
        paths: [../src, ../lib]  # Relative to .praxis-os/
        patterns: ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]
        exclude:
          - "**/node_modules/**"
          - "**/__pycache__/**"
          - "**/venv/**"
          - "**/dist/**"
          - "**/build/**"
          - "**/.git/**"
        debounce_seconds: 10  # Code changes more frequently, longer debounce
```

**Why Longer Debounce for Code:**
- Standards change infrequently (new docs, edits)
- Code changes constantly (every file save during dev)
- 10-second debounce prevents index thrashing
- Still feels responsive (not immediate, but fast enough)

**Validation:**
- Edit standard → index updates in 5 seconds
- Edit code file → index updates in 10 seconds
- Edit excluded file → no update
- Multiple rapid edits → single batched update
- **Add new language to config → watcher picks it up without code change**

**Why Config-Driven Watcher:**

✅ **Language Agnostic:**
```yaml
# Adding Rust support - NO code changes to watcher!
patterns:
  - "*.py"
  - "*.js"
  - "*.rs"  # Just add this line
```

✅ **Project-Specific Flexibility:**
```yaml
# Project A: Python + JavaScript
patterns: ["*.py", "*.js"]
paths: [../src]

# Project B: Full-stack TypeScript + Go backend
patterns: ["*.ts", "*.tsx", "*.go"]
paths: [../frontend/src, ../backend/cmd, ../backend/pkg]
```

✅ **Zero Code Changes:**
- User edits config file
- Restart MCP server (or hot reload config)
- Watcher automatically watches new patterns
- No need to modify watcher.py at all

✅ **Installation Integration:**
```python
# During install, AI detects languages and generates config:
detected_languages = ["python", "javascript", "typescript"]

config["monitoring"]["file_watcher"]["code"]["patterns"] = [
    "*.py", "*.js", "*.ts", "*.jsx", "*.tsx"
]

# Watcher reads this config, knows what to watch
```

**Contrast with Hardcoded Approach:**
```python
# ❌ BAD: Hardcoded (requires code change for new languages)
if file_path.endswith(('.py', '.js', '.ts')):
    rebuild_code_index()
    
# User wants to add Go → must modify watcher.py → breaking change!

# ✅ GOOD: Config-driven (no code change)
for pattern in config['patterns']:
    if fnmatch.fnmatch(file_path, pattern):
        rebuild_code_index()
        
# User wants to add Go → edit config → just works!
```

---

### Phase 7: Installation Integration (1-1.5 hours)

**Goal:** LLM-driven configuration during prAxIs OS installation

**Context:** Installation is conversational - AI agent handles intelligent tasks:
1. User: "Install prAxIs OS from github.com/honeyhiveai/praxis-os"
2. Agent runs install script (mechanical: clone, copy, venv)
3. **Agent analyzes project** (intelligent: language detection)
4. **Agent generates config** (intelligent: index_config.yaml)
5. **Agent manages dependencies** (intelligent: requirements.txt + pip install)
6. Agent builds RAG index (intelligent: triggered by file watcher)

**Tasks:**
1. Update language detection in install workflow (20 min)
   - Detect: Python (.py), JavaScript (.js), TypeScript (.ts), Go (.go), Rust (.rs)
   - Count files per language
   - Determine primary and secondary languages

2. Create config template generator (30 min)
   - Input: detected languages
   - Output: `.praxis-os/config/index_config.yaml` with:
     - Vector/FTS enabled for standards
     - Code search enabled for detected languages
     - Tree-sitter packages listed per language

3. Add dependency installer (30 min)
   - Read `index_config.yaml` code.languages
   - Append to `.praxis-os/mcp_server/requirements.txt`:
     ```
     # Code search dependencies (auto-added during install)
     tree-sitter>=0.21.0
     tree-sitter-python>=0.21.0  # if Python detected
     tree-sitter-javascript>=0.21.0  # if JS detected
     tree-sitter-typescript>=0.21.0  # if TS detected
     ```
   - Re-run pip install in venv

4. Test end-to-end install (20 min)
   - Fresh project with Python + TypeScript
   - Agent detects both languages
   - Config generated with both enabled
   - Dependencies installed
   - Code search works for both

**Validation:** 
- AI agent successfully detects project languages
- Config file reflects detected languages
- Dependencies installed automatically
- Code search works immediately after install

**Installation Flow:**
```
User: "Install prAxIs OS"
  ↓
Script: Clone repo, copy files (mechanical)
  ↓
AI: List project files
AI: Count by extension (.py, .js, .ts)
AI: Determine languages → ["python", "typescript"]
  ↓
AI: Generate config:
    indexes:
      code:
        enabled: true
        languages: [python, typescript]
  ↓
AI: Update requirements.txt:
    tree-sitter>=0.21.0
    tree-sitter-python>=0.21.0
    tree-sitter-typescript>=0.21.0
  ↓
AI: pip install -r requirements.txt
  ↓
AI: Trigger RAG index build (includes code!)
  ↓
User: "Where is StateManager class?" (works immediately!)
```

**Validation:** 
- Installation process intelligently configures code search
- Dependencies match detected languages
- Config reflects project structure
- Code search works immediately after install

### Phase 8: Integration & Testing (1-2 hours)

**Goal:** Everything works together, validated

**Tasks:**
1. Create `pos_search` MCP tool (30 min)
   - Unified tool for all content types
   - content_type: "standards", "code", "dependencies" (future)
   - filters: {domain, phase, role} for standards
   - language detection for code

2. Remove `search_standards` tool (5 min)
   - Clean cutover to pos_search

3. Update documentation (30 min)
   - Tool usage examples
   - Config file reference
   - Installation flow

4. End-to-end testing (45 min)
   - Standards search (hybrid + metadata)
   - Code search (semantic + structure)
   - Performance benchmarks (<200ms target)
   - Accuracy validation (50-70% single-query)

**Validation:** All query types work, latency targets met, accuracy improved over baseline.

---

## ❓ Open Questions

### Q1: Embedding Model Default

**Recommendation:** Use `bge-small-en-v1.5` as default

**Rationale:**
- 10-15% better accuracy than all-MiniLM
- Still fast on CPU (~50-100ms)
- Reasonable size (134MB)
- Supports 33% → 50-60% accuracy goal

**Config allows easy switching:**
- Users can upgrade to bge-base/large for better accuracy
- Users can downgrade to all-MiniLM for minimal footprint
- Future models easy to add (just update config)

**Decision:** ✅ Approved - Use bge-small-en-v1.5 as default

### Q2: Metadata Generation - Rule-Based vs LLM?

**For Universal Standards (60 → 200):**
- Human-authored (framework maintainers)
- High quality, zero API cost
- ~7 hours human time (one-time)

**For Project-Specific Standards (0 → 300+):**
- **Option A:** Rule-based extraction (zero cost, lower quality)
- **Option B:** Optional LLM enhancement (user pays one-time, ~$3 for 300 standards)

**Recommendation:** Ship with rule-based (zero cost), offer LLM as optional enhancement.

**Decision Needed:** Is rule-based "good enough"?

### Q3: Code Languages - How Many Initially?

**Minimum:** Python only (prAxIs OS itself)

**Nice-to-Have:** JavaScript, TypeScript (common in projects)

**Full Support:** Go, Rust, Java, C# (config-driven, add as needed)

**Recommendation:** Ship Python, add JS/TS if time allows, defer others to config additions.

**Decision Needed:** Python-only OK for initial release?

### Q4: Index Rebuild Strategy ✅ ANSWERED

**Current:** Force rebuild drops table (causes corruption if MCP running)

**✅ ANSWER: File locking is sufficient - Blue-green NOT needed**

**Why file locking is better:**
- ✅ **Prevents corruption:** RAG engine holds shared lock, rebuild script needs exclusive lock
- ✅ **Teaches AI:** Blocked rebuild prints informative message about file watcher and correct workflow
- ✅ **Simple:** One lock file, standard Unix mechanism, no state management
- ✅ **Adversarial design:** Prevents wrong action + teaches correct action
- ✅ **Already implemented:** From earlier session (rag-index-rebuild-safety design doc)

**Blue-green drawbacks:**
- ❌ Over-engineering for the problem
- ❌ More code, more failure modes
- ❌ Doesn't teach (silently works or mysteriously fails)
- ❌ State management complexity

**Teaching message when AI tries manual rebuild:**
```
⚠️ MCP server is running with the index open.

File watcher handles incremental updates automatically.

For manual rebuild:
1. Stop MCP server
2. Run: python build_rag_index.py --force
3. Start MCP server

Learn more: search_standards("RAG index rebuilding safety")
```

**Decision:** Ship with file locking only. Blue-green deferred indefinitely (likely not needed).

### Q5: Testing Strategy ✅ ANSWERED

**✅ ANSWER: Systematic approach with ≥80% unit coverage day 1**

**Systematic Testing (from test-generation-js-ts workflow):**

**Phase 1: Code Inventory (15 min)**
- Read all new files (`index_manager.py`, `indexes/base.py`, `indexes/standards_index.py`)
- Inventory all classes, methods, parameters
- Document complexity (async, dependencies, try/catch, etc.)

**Phase 2: Dependency Analysis (15 min)**
- External: `lancedb`, `sentence-transformers`, `yaml`
- Internal: `rag_engine`, config modules
- Mocking strategy: Mock LanceDB tables, mock sentence-transformers model

**Phase 3: Test Plan (15 min)**
- **Unit tests** (≥80% coverage target):
  - IndexManager.__init__ (config loading)
  - IndexManager._init_indexes (index discovery)
  - IndexManager.search (result merging)
  - BaseIndex abstract methods
  - StandardsIndex (moved from RAGEngine)
  
- **Integration tests** (≥60% coverage target):
  - Full search flow (query → results)
  - Config-driven index loading
  - Graceful degradation (missing index)
  
- **E2E tests** (≥70% coverage target):
  - pos_search tool with real queries
  - Hybrid fusion with real data
  - Performance benchmarks

**Phase 4: Test Generation (30 min)**
- Generate unit tests with mocks (pytest fixtures)
- Generate integration tests with real config
- Use test-generation patterns from hive-kube

**Phase 5: Quality Validation (15 min)**
- Pylint: ≥9.0/10 (BLOCKING)
- MyPy: 0 errors (BLOCKING)
- Tests: 100% pass rate (BLOCKING)
- Coverage: Unit ≥80%, Integration ≥60% (BLOCKING)

**Total time:** 1.5 hours per phase

**Decision:** Ship with ≥80% unit coverage. Test generation is a superpower when done systematically!

---

## 🎯 Success Metrics

**Behavioral System Health:**
- [ ] Multi-query pattern still effective at 200+ standards
- [ ] Discovery doesn't degrade below 40% single-query accuracy
- [ ] AI continues querying (doesn't give up)

**Capability Extension:**
- [ ] Can search project code (not just docs)
- [ ] Can verify docs against implementation
- [ ] Code search <200ms latency

**Architecture Quality:**
- [ ] Config-driven (add indexes by editing YAML)
- [ ] Zero breaking changes to existing queries
- [ ] Completes in 12-16 hours (single day)

**Technical Metrics:**
- [ ] Hybrid search: 33% → 50-60% accuracy
- [ ] Metadata filtering: 50% → 70%+ accuracy (with filters)
- [ ] Query latency: <200ms p95
- [ ] Storage: <1.5GB total
- [ ] Memory: <1GB active

---

## 📚 References

**Design Documents:**
- `rag-architecture-scaling-2025-11-01.md` - Strategic roadmap
- `rag-optimization-research-2025-11-01.md` - Industry best practices
- `rag-index-rebuild-safety-2025-11-01.md` - File locking solution

**Standards:**
- `rag-content-authoring.md` - Current RAG optimization
- `query-construction-patterns.md` - How agents query
- `agent-decision-protocol.md` - Behavioral model
- `dogfooding-model.md` - Development workflow

**Related Work:**
- File locking implementation (already designed)
- Multi-agent architecture (secondary agent support)

---

## 📚 Lessons Learned: Why External Research Matters

### The Journey

**Initial Approach (Training Data Assumptions):**
1. "I know how vector DBs work from training"
2. Designed 3-database architecture (LanceDB + rank-bm25 + SQLite)
3. Estimated 12-16 hours implementation
4. Complex integration between systems

**After using `pos_browser` to read LanceDB docs:**
1. Discovered FTS (Full-Text Search) is built-in and BM25-based
2. Discovered scalar indexes (BTREE/BITMAP) for metadata
3. Discovered sub-100ms performance at billions of records
4. **Result:** Simplified to single database, 10-14 hours, better performance

### What Made pos_browser Valuable

**Compared to web_search:**
- Web search → Generic marketing ("LanceDB is fast!")
- pos_browser → Actual API docs (create_fts_index, create_scalar_index)

**Interactive discovery:**
- Navigate docs like a human
- Query for links, follow breadcrumbs
- Extract full content (tables, code examples, config options)

**Speed:**
- Once session open, fast navigation
- Found scalar indexes, FTS capabilities, SQL filtering in minutes

### The Meta-Lesson

This design doc is a **perfect example** of prAxIs OS's core philosophy:

> "Training data ≠ THIS PROJECT's implementation"

**I fell into my own trap:**
- Assumed I knew how to implement hybrid search
- Designed based on "standard patterns" from training data
- Missed that LanceDB had everything built-in

**The fix:**
- Used pos_browser to read actual documentation
- Discovered simpler, better path
- Shipped better architecture in less time

**This is EXACTLY what prAxIs OS teaches AI agents to avoid!**

### Recommendation

**For future AI development:**
- Search standards first (behavioral guidance)
- **Use pos_browser for technical docs** (libraries, APIs, frameworks)
- Validate assumptions with source documentation
- Training data is a starting point, not the answer

**Tools that force external research = Better outcomes.**

---

## ✅ Approval Checklist

Before proceeding to spec creation:

- [ ] Problem statement clear and agreed
- [ ] Goals and non-goals aligned
- [ ] Zero-cost constraint understood
- [ ] Single-day timeline realistic (now 10-14 hours vs 12-16!)
- [ ] Behavioral lens (not just tech) understood
- [ ] Open questions answered
- [ ] Risks acceptable
- [ ] Architecture simplified via research
- [ ] Ready to create formal spec

---

**Next Step:** Upon approval, say "create the spec" to trigger Phase 2 (formal specification using spec_creation workflow).

