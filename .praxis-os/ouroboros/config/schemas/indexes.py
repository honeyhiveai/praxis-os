"""
Configuration schemas for RAG indexes.

Provides Pydantic v2 models for all index configurations:
    - IndexesConfig: Root container for all indexes
    - StandardsIndexConfig: Vector + FTS + reranking for standards
    - CodeIndexConfig: LanceDB + DuckDB for code semantic + graph
    - ASTIndexConfig: Tree-sitter structural search
    - VectorConfig: Vector search configuration
    - FTSConfig: Full-text search configuration
    - RerankingConfig: Cross-encoder reranking
    - GraphConfig: Call graph traversal configuration
    - FileWatcherConfig: File monitoring for incremental updates

All configurations use fail-fast validation with clear error messages.
Cross-field validation ensures semantic constraints (e.g., chunk_overlap < chunk_size).

Example Usage:
    >>> from ouroboros.config.schemas.indexes import IndexesConfig
    >>> 
    >>> config = IndexesConfig(
    ...     standards=StandardsIndexConfig(
    ...         source_paths=["standards/"],
    ...         vector=VectorConfig(chunk_size=500),
    ...         fts=FTSConfig(enabled=True),
    ...     ),
    ...     code=CodeIndexConfig(...),
    ...     ast=ASTIndexConfig(...)
    ... )

See Also:
    - base.BaseConfig: Base configuration model
    - Pydantic v2 validators: https://docs.pydantic.dev/latest/concepts/validators/
"""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator

from ouroboros.config.schemas.base import BaseConfig


class VectorConfig(BaseConfig):
    """
    Vector search configuration using sentence transformers.

    Configures embedding model, chunking strategy, and index type for
    semantic/meaning-based search. Used by both StandardsIndex and CodeIndex.

    Key Settings:
        - model: Sentence transformer model (e.g., "all-MiniLM-L6-v2")
        - chunk_size: Text chunk size in tokens (100-2000)
        - chunk_overlap: Overlap between chunks (0-500, must be < chunk_size)
        - dimension: Embedding dimension (128-4096, model-specific)
        - index_type: Vector index algorithm (HNSW, IVF_PQ, FLAT)

    Chunking Strategy:
        Larger chunks = more context, but less precision
        Smaller chunks = more precision, but less context
        Overlap = prevent concept splitting at boundaries

    Recommended Settings:
        - Standards (docs): chunk_size=800, overlap=100
        - Code (semantic): chunk_size=200, overlap=20

    Example:
        >>> from ouroboros.config.schemas.indexes import VectorConfig
        >>> 
        >>> # Standards config (larger chunks)
        >>> config = VectorConfig(
        ...     model="sentence-transformers/all-MiniLM-L6-v2",
        ...     chunk_size=800,
        ...     chunk_overlap=100,
        ...     dimension=384
        ... )
        >>> 
        >>> # Code config (smaller chunks)
        >>> code_config = VectorConfig(
        ...     model="microsoft/codebert-base",
        ...     chunk_size=200,
        ...     chunk_overlap=20,
        ...     dimension=768
        ... )

    Validation Rules:
        - chunk_size: 100-2000 tokens
        - chunk_overlap: 0-500 tokens, must be < chunk_size
        - dimension: 128-4096 (model-dependent)
        - index_type: Must be HNSW, IVF_PQ, or FLAT
    """

    model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model identifier (HuggingFace model name)",
        min_length=1,
    )

    chunk_size: int = Field(
        default=800,
        ge=100,
        le=2000,
        description="Text chunk size in tokens (100-2000)",
    )

    chunk_overlap: int = Field(
        default=100,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens (0-500)",
    )

    dimension: int = Field(
        default=384,
        ge=128,
        le=4096,
        description="Embedding vector dimension (model-specific)",
    )

    index_type: str = Field(
        default="HNSW",
        pattern=r"^(HNSW|IVF_PQ|FLAT)$",
        description="Vector index algorithm (HNSW=fast, IVF_PQ=compressed, FLAT=exact)",
    )

    @field_validator("chunk_overlap")
    @classmethod
    def validate_overlap_lt_chunk_size(cls, v: int, info) -> int:
        """
        Ensure chunk_overlap is less than chunk_size.

        Prevents configuration error where overlap >= size (invalid chunking).

        Args:
            v: chunk_overlap value
            info: Validation info containing other field values

        Returns:
            int: Validated chunk_overlap

        Raises:
            ValueError: If chunk_overlap >= chunk_size

        Example:
            >>> # Valid: overlap < size
            >>> VectorConfig(chunk_size=800, chunk_overlap=100)  # ✅
            >>> 
            >>> # Invalid: overlap >= size
            >>> VectorConfig(chunk_size=800, chunk_overlap=800)  # ❌ ValueError
        """
        chunk_size = info.data.get("chunk_size", 800)
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) must be < chunk_size ({chunk_size})\n"
                f"Remediation: Set chunk_overlap to < {chunk_size} (recommended: {chunk_size // 8})"
            )
        return v


class FTSConfig(BaseConfig):
    """
    Full-text search (FTS) configuration for keyword matching.

    Configures BM25-based keyword search using LanceDB's native FTS.
    Complements vector search by matching exact terms and phrases.

    Key Settings:
        - enabled: Enable FTS index
        - use_tantivy: Use Tantivy backend (faster, more features)
        - tokenizer: Tokenization strategy

    Tokenizer Options:
        - default: Standard tokenization with stemming
        - standard: Unicode-aware tokenization
        - whitespace: Split on whitespace only
        - simple: Lowercase + split on non-alphanumeric

    Example:
        >>> from ouroboros.config.schemas.indexes import FTSConfig
        >>> 
        >>> # Enable FTS with default tokenizer
        >>> config = FTSConfig(enabled=True, tokenizer="default")
        >>> 
        >>> # Disable FTS (vector-only)
        >>> config = FTSConfig(enabled=False)

    Performance:
        - FTS adds ~10-20ms per query
        - Index size: ~5-10% of corpus size
        - Rebuild time: ~1-2 seconds per 1000 documents
    """

    enabled: bool = Field(
        default=True,
        description="Enable FTS index (keyword matching)",
    )

    use_tantivy: bool = Field(
        default=False,
        description="Use Tantivy backend (faster, more features, requires Rust)",
    )

    tokenizer: str = Field(
        default="default",
        pattern=r"^(default|standard|whitespace|simple)$",
        description="FTS tokenizer (default=stemming, standard=unicode, whitespace=split, simple=lowercase)",
    )


class RerankingConfig(BaseConfig):
    """
    Cross-encoder reranking configuration for result refinement.

    After initial hybrid search (vector + FTS), rerank top-K results using
    a cross-encoder model for improved precision. Adds ~20-50ms per query
    but significantly improves relevance.

    Key Settings:
        - enabled: Enable reranking
        - model: Cross-encoder model (e.g., "ms-marco-MiniLM-L-6-v2")
        - top_k: Rerank top K candidates (5-100)

    When to Enable:
        - Precision matters more than latency
        - Hybrid search returns too many false positives
        - Willing to accept +20-50ms query latency

    Example:
        >>> from ouroboros.config.schemas.indexes import RerankingConfig
        >>> 
        >>> # Enable reranking
        >>> config = RerankingConfig(
        ...     enabled=True,
        ...     model="cross-encoder/ms-marco-MiniLM-L-6-v2",
        ...     top_k=20
        ... )
        >>> 
        >>> # Disable reranking (faster queries)
        >>> config = RerankingConfig(enabled=False)

    Performance Impact:
        - Latency: +20-50ms per query (depends on top_k)
        - Precision improvement: +10-30% (dataset-dependent)
        - Memory: +100-200MB (model loading)
    """

    enabled: bool = Field(
        default=False,
        description="Enable cross-encoder reranking",
    )

    model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Cross-encoder model identifier (HuggingFace model name)",
        min_length=1,
    )

    top_k: int = Field(
        default=20,
        ge=5,
        le=100,
        description="Rerank top K candidates (5-100)",
    )


class ScalarIndexConfig(BaseConfig):
    """
    Configuration for a single scalar index on a metadata column.
    
    Scalar indexes enable fast filtering on metadata fields (e.g., domain, phase, role).
    LanceDB supports two index types:
        - BTREE: For high cardinality columns (many unique values)
        - BITMAP: For low cardinality columns (few unique values, < 1000)
    
    Key Settings:
        - column: Column name to index
        - index_type: BTREE or BITMAP
    
    Example:
        >>> from ouroboros.config.schemas.indexes import ScalarIndexConfig
        >>> 
        >>> # High cardinality (domains: workflow, rag, browser, etc.)
        >>> domain_idx = ScalarIndexConfig(column="domain", index_type="BTREE")
        >>> 
        >>> # Low cardinality (phases: 0-8)
        >>> phase_idx = ScalarIndexConfig(column="phase", index_type="BITMAP")
    
    Performance:
        - BTREE: O(log n) lookups, handles millions of unique values
        - BITMAP: O(1) lookups, best for < 1000 unique values
    """
    
    column: str = Field(
        ...,
        min_length=1,
        description="Column name to index (must exist in data schema)",
    )
    
    index_type: str = Field(
        ...,
        pattern=r"^(BTREE|BITMAP|btree|bitmap)$",
        description="Index type: BTREE (high cardinality) or BITMAP (low cardinality)",
    )


class MetadataFilteringConfig(BaseConfig):
    """
    Metadata filtering configuration for pre/post-filtering search results.
    
    Enables filtering search results by metadata fields (e.g., domain, phase, role).
    Requires scalar indexes on filtered columns for performance.
    
    Key Settings:
        - enabled: Enable metadata filtering
        - scalar_indexes: List of scalar indexes to create
        - auto_generate: Auto-detect columns and generate indexes
        - llm_enhance: Use LLM to extract additional metadata
    
    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     MetadataFilteringConfig, ScalarIndexConfig
        ... )
        >>> 
        >>> config = MetadataFilteringConfig(
        ...     enabled=True,
        ...     scalar_indexes=[
        ...         ScalarIndexConfig(column="domain", index_type="BTREE"),
        ...         ScalarIndexConfig(column="phase", index_type="BITMAP"),
        ...         ScalarIndexConfig(column="role", index_type="BITMAP"),
        ...     ],
        ...     auto_generate=False,
        ...     llm_enhance=False
        ... )
    
    Filtering Usage:
        >>> # Filter by phase
        >>> results = search_standards(
        ...     query="workflow execution",
        ...     filters={"phase": 3}
        ... )
        >>> 
        >>> # Filter by multiple criteria
        >>> results = search_standards(
        ...     query="error handling",
        ...     filters={"domain": "workflow", "role": "agent"}
        ... )
    """
    
    enabled: bool = Field(
        default=False,
        description="Enable metadata filtering",
    )
    
    scalar_indexes: list["ScalarIndexConfig"] = Field(
        default_factory=list,
        description="Scalar indexes to create for filtering",
    )
    
    auto_generate: bool = Field(
        default=False,
        description="Auto-detect columns and generate scalar indexes",
    )
    
    llm_enhance: bool = Field(
        default=False,
        description="Use LLM to extract additional metadata from content",
    )


class GraphConfig(BaseConfig):
    """
    Graph traversal configuration for call graph analysis.

    Configures DuckDB recursive CTEs for call graph queries:
        - find_callers: Who calls this function?
        - find_dependencies: What does this function call?
        - find_call_paths: Show call chain from A to B

    Key Settings:
        - max_depth: Maximum recursion depth (1-100)
        - relationship_types: Relationship types to track

    Relationship Types:
        - calls: Function/method calls
        - imports: Module imports
        - inherits: Class inheritance

    Example:
        >>> from ouroboros.config.schemas.indexes import GraphConfig
        >>> 
        >>> config = GraphConfig(
        ...     max_depth=10,
        ...     relationship_types=["calls", "imports", "inherits"]
        ... )

    Performance:
        - Shallow graphs (depth 1-3): <10ms
        - Medium graphs (depth 4-7): 10-50ms
        - Deep graphs (depth 8-10): 50-200ms

    Security:
        max_depth prevents infinite recursion in circular call graphs.
    """

    max_depth: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Max recursion depth for CTE queries (prevents infinite loops)",
    )

    relationship_types: list[str] = Field(
        default=["calls", "imports", "inherits"],
        description="Relationship types to track in graph",
        min_length=1,
    )


class FileWatcherConfig(BaseConfig):
    """
    File watcher configuration for incremental index updates.

    Monitors configured paths for file changes and triggers incremental
    re-indexing. Debouncing prevents rebuild storms during rapid changes.

    Key Settings:
        - enabled: Enable file watching
        - debounce_ms: Debounce delay in milliseconds
        - watch_patterns: File patterns to watch

    Debouncing Strategy:
        - Standards (markdown): 2000ms (docs change less frequently)
        - Code (Python/TS): 3000ms (code changes in bursts)

    Example:
        >>> from ouroboros.config.schemas.indexes import FileWatcherConfig
        >>> 
        >>> config = FileWatcherConfig(
        ...     enabled=True,
        ...     debounce_ms=2000,
        ...     watch_patterns=["*.md", "*.py", "*.ts"]
        ... )

    Performance:
        - Monitoring overhead: <1% CPU
        - Update latency: debounce_ms + rebuild time
        - Rebuild time: <5s for incremental updates
    """

    enabled: bool = Field(
        default=True,
        description="Enable file watching for incremental updates",
    )

    debounce_ms: int = Field(
        default=500,
        ge=100,
        le=5000,
        description="Debounce delay in milliseconds (prevents rebuild storms)",
    )

    watch_patterns: list[str] = Field(
        default=["*.md", "*.py", "*.go", "*.rs", "*.ts", "*.tsx"],
        description="File patterns to watch (glob patterns)",
        min_length=1,
    )


class StandardsIndexConfig(BaseConfig):
    """
    Configuration for standards index (documentation/markdown files).

    Implements hybrid search (vector + FTS + RRF) with optional reranking
    for searching project standards, docs, and knowledge base.

    Key Settings:
        - source_paths: Directories to index (relative to .praxis-os/)
        - vector: Vector search configuration
        - fts: Full-text search configuration
        - reranking: Optional cross-encoder reranking

    Search Strategy:
        1. Vector search: Semantic/meaning-based matching
        2. FTS: Keyword/exact term matching
        3. RRF: Reciprocal Rank Fusion (merge results)
        4. Rerank: Optional cross-encoder refinement

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     StandardsIndexConfig, VectorConfig, FTSConfig
        ... )
        >>> 
        >>> config = StandardsIndexConfig(
        ...     source_paths=["standards/", "docs/"],
        ...     vector=VectorConfig(chunk_size=800, chunk_overlap=100),
        ...     fts=FTSConfig(enabled=True),
        ...     reranking=None  # Disable reranking
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - reranking: Optional (None = disabled)
    """

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Directories to index (relative to .praxis-os/)",
    )

    vector: VectorConfig = Field(
        ...,
        description="Vector search configuration",
    )

    fts: FTSConfig = Field(
        ...,
        description="Full-text search configuration",
    )

    reranking: Optional[RerankingConfig] = Field(
        default=None,
        description="Optional cross-encoder reranking (None = disabled)",
    )

    metadata_filtering: MetadataFilteringConfig = Field(
        default_factory=lambda: MetadataFilteringConfig(enabled=False),
        description="Metadata filtering configuration for pre/post-filtering",
    )



class CodeIndexConfig(BaseConfig):
    """
    Configuration for code index (LanceDB semantic + DuckDB graph).

    Dual-index system for code search:
        - LanceDB: Semantic code search (vector + FTS + hybrid)
        - DuckDB: Call graph traversal (recursive CTEs)

    Key Settings:
        - source_paths: Code directories to index
        - languages: Programming languages to support
        - vector: Vector search config (CodeBERT)
        - fts: Full-text search config
        - duckdb_path: DuckDB database path
        - graph: Graph traversal config

    Supported Languages:
        - Python, TypeScript, JavaScript, Go, Rust
        - Config-driven: Add via YAML, no code changes

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     CodeIndexConfig, VectorConfig, FTSConfig, GraphConfig
        ... )
        >>> 
        >>> config = CodeIndexConfig(
        ...     source_paths=["src/", "lib/"],
        ...     languages=["python", "typescript"],
        ...     vector=VectorConfig(
        ...         model="microsoft/codebert-base",
        ...         chunk_size=200,
        ...         dimension=768
        ...     ),
        ...     fts=FTSConfig(enabled=True),
        ...     duckdb_path=Path(".praxis-os/code.duckdb"),
        ...     graph=GraphConfig(max_depth=10)
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - languages: At least one language required
    """

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Code directories to index (e.g., ['src/', 'lib/'])",
    )

    languages: list[str] = Field(
        ...,
        min_length=1,
        description="Programming languages to support (e.g., ['python', 'typescript'])",
    )

    vector: VectorConfig = Field(
        ...,
        description="Vector search configuration (recommend CodeBERT)",
    )

    fts: FTSConfig = Field(
        ...,
        description="Full-text search configuration",
    )

    duckdb_path: Path = Field(
        default=Path(".praxis-os/code.duckdb"),
        description="DuckDB database path for call graph",
    )

    graph: GraphConfig = Field(
        ...,
        description="Graph traversal configuration",
    )

    respect_gitignore: bool = Field(
        default=True,
        description="Respect .gitignore patterns when indexing files (recommended: True)",
    )

    exclude_patterns: Optional[list[str]] = Field(
        default=None,
        description="Additional exclusion patterns in gitignore format (merged with .gitignore if present)",
    )



class ASTIndexConfig(BaseConfig):
    """
    Configuration for AST index (Tree-sitter structural search).

    Parses source code into Abstract Syntax Trees for structural queries:
        - Find all async functions
        - Find all classes with specific methods
        - Find all error handling blocks

    Key Settings:
        - source_paths: Code directories to parse
        - languages: Languages to support (Tree-sitter parsers)
        - auto_install_parsers: Auto-install missing parsers
        - venv_path: Isolated venv for parser installation

    Auto-Install Behavior:
        If enabled, server will `pip install tree-sitter-{language}` for
        any missing parser on startup. Requires internet access.

    Example:
        >>> from ouroboros.config.schemas.indexes import ASTIndexConfig
        >>> 
        >>> config = ASTIndexConfig(
        ...     source_paths=["src/", "lib/"],
        ...     languages=["python", "typescript", "rust"],
        ...     auto_install_parsers=True,
        ...     venv_path=Path(".praxis-os/venv")
        ... )

    Validation Rules:
        - source_paths: At least one path required
        - languages: At least one language required

    Security:
        Parser installation uses isolated venv (no system pollution).
    """

    source_paths: list[str] = Field(
        ...,
        min_length=1,
        description="Code directories to parse (e.g., ['src/', 'lib/'])",
    )

    languages: list[str] = Field(
        ...,
        min_length=1,
        description="Languages to support (e.g., ['python', 'typescript'])",
    )

    auto_install_parsers: bool = Field(
        default=True,
        description="Auto-install missing Tree-sitter parsers (requires internet)",
    )

    venv_path: Path = Field(
        default=Path(".praxis-os/venv"),
        description="Isolated venv for parser installation",
    )



class IndexesConfig(BaseConfig):
    """
    Root configuration for all RAG indexes.

    Composes StandardsIndex, CodeIndex, and ASTIndex configurations with
    shared settings for caching and file watching.

    Key Settings:
        - standards: Standards index configuration
        - code: Code index configuration
        - ast: AST index configuration
        - cache_path: Base cache path for all indexes
        - file_watcher: File monitoring configuration

    Cache Structure:
        .praxis-os/.cache/indexes/
        ├── standards/        # Standards vector index (LanceDB)
        ├── code/             # Code vector index (LanceDB) + graph (DuckDB)
        └── ast/              # AST index (SQLite)

    Example:
        >>> from ouroboros.config.schemas.indexes import (
        ...     IndexesConfig, StandardsIndexConfig, CodeIndexConfig, ASTIndexConfig
        ... )
        >>> 
        >>> config = IndexesConfig(
        ...     standards=StandardsIndexConfig(...),
        ...     code=CodeIndexConfig(...),
        ...     ast=ASTIndexConfig(...),
        ...     cache_path=Path(".cache/indexes"),  # Relative to base_path
        ...     file_watcher=FileWatcherConfig(enabled=True)
        ... )

    Validation:
        All nested configs are validated on creation (fail-fast).
    """

    standards: StandardsIndexConfig = Field(
        ...,
        description="Standards index configuration",
    )

    code: CodeIndexConfig = Field(
        ...,
        description="Code index configuration",
    )

    ast: ASTIndexConfig = Field(
        ...,
        description="AST index configuration",
    )

    cache_path: Path = Field(
        default=Path(".cache/indexes"),
        description="Base cache path for all indexes (relative to base_path)",
    )

    file_watcher: FileWatcherConfig = Field(
        ...,
        description="File watcher configuration",
    )


__all__ = [
    "VectorConfig",
    "FTSConfig",
    "RerankingConfig",
    "GraphConfig",
    "FileWatcherConfig",
    "StandardsIndexConfig",
    "CodeIndexConfig",
    "ASTIndexConfig",
    "IndexesConfig",
]

