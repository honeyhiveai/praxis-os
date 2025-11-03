"""Standards index implementation for prAxIs OS standards search.

This module provides StandardsIndex, which implements vector-based semantic
search over prAxIs OS markdown standards using LanceDB and sentence-transformers.

The index currently supports:
- Vector similarity search with BGE embeddings
- Metadata filtering (phase, framework_type, tags, is_critical)
- Query result caching with TTL
- Graceful degradation to grep fallback
- Thread-safe hot reload for file watcher integration

Future enhancements (Phase 2):
- Full-Text Search (FTS) with BM25
- Hybrid search with Reciprocal Rank Fusion (RRF)
- Cross-encoder re-ranking

Example:
    >>> from pathlib import Path
    >>> index = StandardsIndex(
    ...     cache_path=Path(".praxis-os/.cache/standards"),
    ...     config={"embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}}
    ... )
    >>> 
    >>> # Build index from markdown files
    >>> index.build(source_paths=[".praxis-os/standards"], force=False)
    >>> 
    >>> # Search with metadata filter
    >>> results = index.search(
    ...     query="authentication security best practices",
    ...     filters={"phase": 0, "is_critical": True},
    ...     n=5
    ... )
    >>> for r in results:
    ...     print(f"{r.relevance_score:.2f}: {r.file_path}")
"""

import fcntl
import hashlib
import json
import logging
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import lancedb
from sentence_transformers import SentenceTransformer

from .base import BaseIndex, SearchResult

logger = logging.getLogger(__name__)


class StandardsIndex(BaseIndex):
    """Vector-based semantic search for prAxIs OS standards.
    
    This index uses LanceDB for vector storage and sentence-transformers (BGE)
    for generating embeddings. It provides semantic search with metadata filtering
    and falls back to grep if vector search is unavailable.
    
    The implementation uses file locking (`fcntl`) to prevent concurrent index
    rebuilds, ensuring data integrity during hot reload operations.
    
    Thread Safety:
        - All public methods are thread-safe via RLock
        - Hot reload blocks queries until completion
        - Cache operations are protected by lock
        - File lock prevents concurrent builds
    
    Attributes:
        cache_path: Directory for LanceDB index storage
        config: Configuration dictionary with embedding and cache settings
        table: LanceDB table instance (None if unavailable)
        db: LanceDB connection (None if unavailable)
        vector_search_available: Whether vector search is initialized
        local_model: SentenceTransformer model instance for local embeddings
        
    Example:
        >>> config = {
        ...     "embedding": {
        ...         "provider": "local",
        ...         "model": "all-MiniLM-L6-v2"
        ...     },
        ...     "cache": {
        ...         "enabled": True,
        ...         "ttl_seconds": 3600
        ...     },
        ...     "source_paths": [".praxis-os/standards"]
        ... }
        >>> index = StandardsIndex(cache_path, config)
        >>> results = index.search("how to build workflows", filters={}, n=5)
    """
    
    def __init__(self, cache_path: Path, config: dict):
        """Initialize StandardsIndex with configuration.
        
        Args:
            cache_path: Path to directory for index storage. Will create
                subdirectory for LanceDB tables.
            config: Configuration dictionary with keys:
                - embedding.provider: "local" or "openai"
                - embedding.model: Model name (default: "all-MiniLM-L6-v2")
                - cache.enabled: Enable query caching (default: True)
                - cache.ttl_seconds: Cache TTL in seconds (default: 3600)
                - source_paths: List of paths to index (for documentation)
        
        Raises:
            ValueError: If config is invalid or missing required fields
            RuntimeError: If embedding model initialization fails
        
        Note:
            The index is not built until build() is called explicitly.
        """
        self.cache_path = cache_path
        self.config = config
        
        # Validate config (supports both old and new structure)
        # New structure: config['vector'] (content-type oriented)
        # Old structure: config['embedding'] (feature oriented)
        if "vector" in config:
            embedding_config = config["vector"]
        elif "embedding" in config:
            embedding_config = config["embedding"]
        else:
            raise ValueError("Config missing 'vector' or 'embedding' section")
        
        # Extract embedding configuration from nested structure
        self.embedding_provider = embedding_config.get("provider", "local")
        self.embedding_model = embedding_config.get("model", "all-MiniLM-L6-v2")
        
        # Extract cache configuration
        cache_config = config.get("cache", {})
        self.cache_enabled = cache_config.get("enabled", True)
        self.cache_ttl_seconds = cache_config.get("ttl_seconds", 3600)
        
        # Query cache: {query_hash: (List[SearchResult], timestamp)}
        self._query_cache: Dict[str, tuple] = {}
        
        # Concurrency control
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        self._rebuilding = threading.Event()  # Signal when rebuild in progress
        
        # Initialize embedding model
        self.local_model: Any = None
        if self.embedding_provider == "local":
            try:
                logger.info("Loading embedding model: %s", self.embedding_model)
                self.local_model = SentenceTransformer(self.embedding_model)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error("Failed to load embedding model: %s", e)
                raise RuntimeError(f"Embedding model initialization failed: {e}") from e
        
        # LanceDB connection (initialized lazily in build())
        self.db: Any = None
        self.table: Any = None
        self.vector_search_available = False
        self._lock_file: Any = None
        
        # Create cache directory
        self.cache_path.mkdir(parents=True, exist_ok=True)
        logger.info("StandardsIndex initialized at %s", cache_path)
    
    def build(self, source_paths: List[str], force: bool = False, incremental: bool = True) -> None:
        """Build or rebuild the index from source markdown files.
        
        This method processes markdown files from source_paths, generates
        embeddings, and creates a LanceDB table with vector index. It uses
        file locking to prevent concurrent builds.
        
        Supports incremental updates by tracking file modification times and only
        processing changed/new files.
        
        Args:
            source_paths: List of directory or file paths containing markdown
                standards to index. Paths can be absolute or relative.
            force: If True, rebuild index even if it exists. If False,
                skip build if index is already present.
            incremental: If True, use incremental updates (only process changed files).
                Ignored if force=True or index doesn't exist.
        
        Raises:
            RuntimeError: If build fails (file lock contention, LanceDB error, etc.)
        
        Example:
            >>> index.build(
            ...     source_paths=[".praxis-os/standards"],
            ...     force=True  # Force full rebuild
            ... )
            >>> index.build(
            ...     source_paths=[".praxis-os/standards"],
            ...     incremental=True  # Only process changed files
            ... )
        """
        logger.info("Build requested for StandardsIndex (force=%s, incremental=%s)", force, incremental)
        logger.info("Source paths: %s", source_paths)
        
        # Convert source_paths to Path objects
        source_path_objs = [Path(p) for p in source_paths]
        
        # Check if index already exists
        index_path = self.cache_path / "praxis_os_standards.lance"
        table_exists = index_path.exists()
        
        # Determine build strategy
        use_incremental = incremental and table_exists and not force
        
        if use_incremental:
            logger.info("📝 Using incremental update (only processing changed files)")
            self._connect_to_index()  # Ensure we're connected to existing table
            
            changed_files = self._get_changed_files(source_path_objs)
            
            if not changed_files:
                logger.info("No files changed, index is up to date")
                return
            
            logger.info(f"Found {len(changed_files)} changed files to process")
            files_to_process = changed_files
            
            # Note: _get_changed_files() already called remove_file() for deleted files
            # and remove_file() for changed files will happen below before adding new chunks
            
            # Delete old chunks for changed files before adding new ones
            logger.info("🗑️  Removing old chunks for changed files...")
            for file_path in changed_files:
                self.remove_file(str(file_path.resolve()))
        elif not force and table_exists:
            logger.info("Index already exists, skipping build (use force=True to rebuild)")
            self._connect_to_index()
            return
        else:
            if force:
                logger.info("🔄 Force rebuild requested - processing all files")
            else:
                logger.info("🔄 Initial build - processing all files")
            
            # Collect all markdown files from source paths
            files_to_process = []
            for source_path in source_path_objs:
                files_to_process.extend(list(source_path.rglob("*.md")))
            
            if not files_to_process:
                logger.warning("No markdown files found in source paths")
                return
            
            logger.info(f"Processing {len(files_to_process)} total files")
        
        # Import chunker (lazy import to avoid circular dependencies)
        try:
            from mcp_server.chunker import AgentOSChunker
        except ImportError:
            # Fallback for direct execution context
            import sys
            from pathlib import Path as ImportPath
            chunker_path = ImportPath(__file__).parent.parent.parent / "chunker.py"
            import importlib.util as import_util
            spec = import_util.spec_from_file_location("chunker", chunker_path)
            if spec is None or spec.loader is None:
                raise RuntimeError(f"Failed to load chunker module from {chunker_path}")
            chunker_module = import_util.module_from_spec(spec)
            sys.modules['chunker'] = chunker_module
            spec.loader.exec_module(chunker_module)
            AgentOSChunker = chunker_module.AgentOSChunker
        
        # Acquire file lock to prevent concurrent builds
        lock_file_path = self.cache_path / ".index.lock"
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        lock_fd = None
        try:
            logger.info("Acquiring index build lock: %s", lock_file_path)
            lock_fd = open(lock_file_path, 'w', encoding='utf-8')
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("Lock acquired, starting build")
            
            # Step 1: Chunk markdown files
            logger.info("Step 1/5: Chunking %d markdown files", len(files_to_process))
            chunker = AgentOSChunker()
            all_chunks = []
            
            for file_path in files_to_process:
                if not file_path.exists():
                    logger.warning("File does not exist: %s", file_path)
                    continue
                
                if file_path.is_file() and file_path.suffix == '.md':
                    chunks = chunker.chunk_file(file_path)
                    all_chunks.extend(chunks)
                else:
                    logger.warning("Skipping non-markdown file: %s", file_path)
                    continue
            
            if not all_chunks:
                logger.warning("No chunks generated from files")
                if use_incremental:
                    # For incremental, this might be OK (e.g., empty files)
                    return
                else:
                    raise RuntimeError("No chunks generated from source paths")
            
            logger.info("Chunked %d markdown files into %d chunks", len(files_to_process), len(all_chunks))
            
            # Step 2: Generate embeddings
            logger.info("Step 2/5: Generating embeddings for %d chunks", len(all_chunks))
            if not self.local_model:
                raise RuntimeError("Embedding model not initialized")
            
            # Extract content for embedding
            contents = [chunk.content for chunk in all_chunks]
            embeddings = self.local_model.encode(
                contents,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            logger.info("Generated %d embeddings", len(embeddings))
            
            # Step 3: Prepare data for LanceDB
            logger.info("Step 3/5: Preparing LanceDB records")
            records = []
            for chunk, embedding in zip(all_chunks, embeddings):
                record = {
                    "content": chunk.content,
                    "vector": embedding.tolist(),
                    "file_path": chunk.file_path,
                    "chunk_id": chunk.chunk_id,
                    "section_header": chunk.section_header,
                    "token_count": chunk.tokens,
                    # Metadata fields (flat for scalar indexing)
                    "framework_type": chunk.metadata.framework_type,
                    "phase": chunk.metadata.phase if chunk.metadata.phase is not None else -1,
                    "is_critical": chunk.metadata.is_critical,
                    "tags": json.dumps(chunk.metadata.tags),  # JSON string for LanceDB
                }
                records.append(record)
            
            logger.info("Prepared %d records for indexing", len(records))
            
            # Step 4: Create/update LanceDB table
            logger.info("Step 4/5: Creating/updating LanceDB table")
            self.db = lancedb.connect(str(self.cache_path))
            
            if use_incremental:
                # Add new records to existing table
                logger.info(f"➕ Adding {len(records)} new/updated records to existing table...")
                self.table.add(records)
                total_chunks = self.table.count_rows()
                logger.info(f"✅ Table updated - now contains {total_chunks} total records")
            else:
                # Full rebuild - drop and recreate table
                try:
                    if force or table_exists:
                        self.db.drop_table("praxis_os_standards")
                        logger.info("Dropped existing table for full rebuild")
                except Exception:
                    pass  # Table doesn't exist, that's fine
                
                # Create new table with vector data
                self.table = self.db.create_table(
                    "praxis_os_standards",
                    data=records,
                    mode="overwrite"
                )
                logger.info("Created LanceDB table with %d records", len(records))
            
            # Step 5: Create indexes (FTS and scalar)
            logger.info("Step 5/5: Creating FTS and scalar indexes")
            
            # FTS index for keyword search (idempotent)
            self._ensure_fts_index()
            
            # Scalar indexes for metadata filtering
            self._create_scalar_indexes()
            
            # Save file mtimes for next incremental build
            self._save_file_mtimes(source_path_objs)
            
            logger.info("✅ Index build complete: %d chunks indexed", len(all_chunks))
            self.vector_search_available = True
            
        except BlockingIOError as e:
            logger.error("Index lock held by another process")
            raise RuntimeError(
                "Cannot build index: another process holds the lock. "
                "Stop MCP server or wait for other build to complete."
            ) from e
        except Exception as e:
            logger.error("Index build failed: %s", e, exc_info=True)
            raise RuntimeError(f"Index build failed: {e}") from e
        finally:
            # Release lock
            if lock_fd:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                    logger.info("Index lock released")
                except Exception as e:
                    logger.warning("Failed to release lock: %s", e)
    
    def _get_changed_files(self, source_paths: List[Path]) -> List[Path]:
        """Get list of files that changed since last build.
        
        Compares current file modification times against stored metadata
        to detect new, modified, or deleted files.
        
        Args:
            source_paths: Paths to scan for markdown files
        
        Returns:
            List of file paths that need reprocessing
        """
        metadata_file = self.cache_path / "metadata.json"
        
        # No metadata = all files are "changed" (first build)
        if not metadata_file.exists():
            all_files = []
            for source_path in source_paths:
                all_files.extend(list(source_path.rglob("*.md")))
            return all_files
        
        try:
            metadata = json.loads(metadata_file.read_text())
            file_mtimes = metadata.get("files_mtimes", {})
            
            changed_files = []
            current_files = set()
            
            for source_path in source_paths:
                for md_file in source_path.rglob("*.md"):
                    file_path_str = str(md_file.resolve())
                    current_files.add(file_path_str)
                    current_mtime = md_file.stat().st_mtime
                    
                    # File is new or modified
                    if (
                        file_path_str not in file_mtimes
                        or file_mtimes[file_path_str] != current_mtime
                    ):
                        changed_files.append(md_file)
                        logger.debug(
                            "File changed: %s (old_mtime=%s, new_mtime=%s)",
                            md_file.name,
                            file_mtimes.get(file_path_str, "N/A"),
                            current_mtime
                        )
            
            # Check for deleted files
            deleted_files = set(file_mtimes.keys()) - current_files
            if deleted_files:
                logger.info("Found %d deleted files to remove from index", len(deleted_files))
                for deleted_file in deleted_files:
                    self.remove_file(deleted_file)
            
            return changed_files
            
        except Exception as e:
            logger.error("Failed to load metadata, treating all files as changed: %s", e)
            all_files = []
            for source_path in source_paths:
                all_files.extend(list(source_path.rglob("*.md")))
            return all_files
    
    def _save_file_mtimes(self, source_paths: List[Path]) -> None:
        """Save file modification times to metadata for change detection.
        
        Args:
            source_paths: Paths to scan for markdown files
        """
        metadata_file = self.cache_path / "metadata.json"
        
        # Collect all file mtimes
        file_mtimes = {}
        for source_path in source_paths:
            for md_file in source_path.rglob("*.md"):
                file_path_str = str(md_file.resolve())
                file_mtimes[file_path_str] = md_file.stat().st_mtime
        
        # Load existing metadata or create new
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())
            except Exception:
                metadata = {}
        else:
            metadata = {}
        
        # Update with current file mtimes
        metadata["files_mtimes"] = file_mtimes
        metadata["last_updated"] = datetime.now().isoformat()
        
        # Save metadata
        metadata_file.write_text(json.dumps(metadata, indent=2))
        logger.debug("Saved file modification times for %d files", len(file_mtimes))
    
    def remove_file(self, file_path: str) -> None:
        """Remove all chunks from a deleted file from the index.
        
        When a markdown file is deleted, this method removes all its chunks
        from the LanceDB table to keep the index synchronized with the filesystem.
        
        Args:
            file_path: Absolute or relative path to the deleted file
        
        Note:
            This method is thread-safe and uses row-level deletion in LanceDB.
            If the table doesn't exist or the file wasn't indexed, this is a no-op.
        
        Example:
            >>> index.remove_file(".praxis-os/standards/old-doc.md")
        """
        if not self.table:
            logger.warning("Cannot remove file: index not initialized")
            return
        
        try:
            # Normalize path for comparison (handle both relative and absolute)
            file_path_obj = Path(file_path)
            if not file_path_obj.is_absolute():
                file_path_obj = file_path_obj.resolve()
            file_path_str = str(file_path_obj)
            
            logger.info("Removing chunks for deleted file: %s", file_path_str)
            
            # Query to find matching chunks
            # LanceDB delete uses SQL WHERE syntax
            delete_result = self.table.delete(f"file_path = '{file_path_str}'")
            
            # LanceDB delete() returns DeleteResult object with num_deleted attribute
            deleted_count = getattr(delete_result, 'num_deleted', 0) if delete_result else 0
            
            if deleted_count > 0:
                logger.info("✅ Removed %d chunks for file: %s", deleted_count, file_path_str)
                # Invalidate cache since index changed
                with self._lock:
                    self._query_cache.clear()
            else:
                logger.debug("No chunks found for file: %s", file_path_str)
        
        except Exception as e:
            logger.error("Failed to remove file from index: %s", e, exc_info=True)
            # Don't raise - deletion is best-effort
    
    def _create_scalar_indexes(self) -> None:
        """Create scalar indexes for metadata filtering.
        
        Creates BTREE and BITMAP indexes on metadata fields to enable efficient
        pre-filtering before vector search. This dramatically improves search
        accuracy by reducing the search space.
        
        Indexes created:
            - framework_type: BTREE (high cardinality - many unique values)
            - phase: BITMAP (low cardinality - only 0-8 values)
            - is_critical: BITMAP (low cardinality - boolean)
        
        Note:
            Scalar indexes are idempotent - LanceDB handles duplicate creation.
            Total index size is typically <10MB for 500 standards corpus.
        
        Raises:
            RuntimeError: If scalar index creation fails critically
        """
        try:
            # BTREE index for high-cardinality field (many unique framework types)
            logger.info("Creating BTREE scalar index on 'framework_type'...")
            try:
                self.table.create_scalar_index("framework_type", index_type="BTREE")
                logger.info("✅ BTREE index created on 'framework_type'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.debug("Scalar index on 'framework_type' already exists")
                else:
                    logger.warning("Failed to create BTREE index on 'framework_type': %s", e)
            
            # BITMAP index for low-cardinality field (phase: 0-8)
            logger.info("Creating BITMAP scalar index on 'phase'...")
            try:
                self.table.create_scalar_index("phase", index_type="BITMAP")
                logger.info("✅ BITMAP index created on 'phase'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.debug("Scalar index on 'phase' already exists")
                else:
                    logger.warning("Failed to create BITMAP index on 'phase': %s", e)
            
            # BITMAP index for boolean field
            logger.info("Creating BITMAP scalar index on 'is_critical'...")
            try:
                self.table.create_scalar_index("is_critical", index_type="BITMAP")
                logger.info("✅ BITMAP index created on 'is_critical'")
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.debug("Scalar index on 'is_critical' already exists")
                else:
                    logger.warning("Failed to create BITMAP index on 'is_critical': %s", e)
            
            logger.info("✅ Scalar index creation complete")
            
        except Exception as e:
            logger.error("Scalar index setup failed: %s", e)
            # Don't fail build if scalar indexes fail
            # System can still operate with unfiltered search
            logger.warning("Proceeding without scalar indexes (unfiltered search)")
    
    def _ensure_fts_index(self) -> None:
        """Ensure FTS (Full-Text Search) index exists on content column.
        
        Creates LanceDB FTS index using BM25 algorithm for keyword-based search.
        This is idempotent - safely skips if FTS index already exists.
        
        FTS index enables hybrid search (vector + keyword) for improved accuracy.
        
        Raises:
            RuntimeError: If FTS index creation fails
        
        Note:
            FTS index size is typically <50MB for 500 standards corpus.
            BM25 scoring is handled natively by LanceDB.
        """
        try:
            # Check if FTS index already exists
            # LanceDB will raise if we try to create duplicate FTS index
            # So we wrap in try/except for idempotency
            try:
                logger.info("Creating FTS index on 'content' column...")
                self.table.create_fts_index("content", use_tantivy=False)
                logger.info("✅ FTS index created successfully (BM25-based)")
            except Exception as create_error:
                # Check if error is due to existing index
                error_msg = str(create_error).lower()
                if "already exists" in error_msg or "fts index" in error_msg:
                    logger.debug("FTS index already exists, skipping creation")
                else:
                    # Unexpected error, re-raise
                    raise RuntimeError(f"FTS index creation failed: {create_error}") from create_error

        except Exception as e:
            logger.error("FTS index setup failed: %s", e)
            # Don't fail connection if FTS index creation fails
            # System can still operate with vector search only
            logger.warning("Proceeding without FTS index (vector search only)")
    
    def _connect_to_index(self) -> None:
        """Connect to existing LanceDB index with file locking.
        
        Raises:
            RuntimeError: If connection fails
        """
        index_path = self.cache_path / "praxis_os_standards.lance"
        
        if not index_path.exists():
            raise RuntimeError(f"Index not found at {index_path}")
        
        try:
            logger.info("Connecting to LanceDB index at %s", self.cache_path)
            self.db = lancedb.connect(str(self.cache_path))
            self.table = self.db.open_table("praxis_os_standards")
            chunk_count = self.table.count_rows()
            logger.info("LanceDB table loaded: %s chunks", chunk_count)
            self.vector_search_available = True
            
            # Create FTS index if it doesn't exist (Phase 2, Task 2.1)
            self._ensure_fts_index()
            
            # Acquire shared lock to prevent concurrent full rebuilds
            lock_file_path = self.cache_path / ".standards.lock"
            self._lock_file = open(lock_file_path, 'w', encoding='utf-8')
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_SH)
            logger.debug("Acquired shared lock on index")
            
        except Exception as e:
            logger.error("Failed to connect to LanceDB: %s", e)
            self.vector_search_available = False
            if self._lock_file:
                try:
                    self._lock_file.close()
                except Exception:
                    pass
                self._lock_file = None
            raise
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n: int = 5
    ) -> List[SearchResult]:
        """Search standards with vector similarity and metadata filtering.
        
        Performs semantic search using query embeddings and returns top n
        results sorted by relevance. Supports metadata filters for precise
        retrieval (phase, framework_type, tags, is_critical).
        
        If vector search is unavailable, falls back to grep-based search.
        
        Args:
            query: Natural language search query
            filters: Optional metadata filters:
                - phase: int (phase number to filter by)
                - framework_type: str (framework type)
                - tags: List[str] (tags to filter by)
                - is_critical: bool (only critical content)
            n: Number of results to return (default: 5)
        
        Returns:
            List of SearchResult objects sorted by relevance_score descending.
            Empty list if no matches found.
        
        Raises:
            ValueError: If query is empty or n < 1
            RuntimeError: If search fails unexpectedly
        
        Example:
            >>> results = index.search(
            ...     query="Phase 1 verification requirements",
            ...     filters={"phase": 1, "is_critical": True},
            ...     n=5
            ... )
            >>> for r in results:
            ...     print(f"{r.relevance_score:.2f}: {r.file_path}")
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n}")
        
        # Wait if rebuild in progress (timeout: 30s)
        if self._rebuilding.is_set():
            logger.debug("Waiting for index rebuild to complete...")
            if not self._rebuilding.wait(timeout=30):
                logger.warning("Rebuild timeout, proceeding with current index")
        
        start_time = time.time()
        
        # Check cache
        cache_key = ""  # Initialize to empty string
        if self.cache_enabled:
            cache_key = self._generate_cache_key(query, filters, n)
            cached_results = self._check_cache(cache_key)
            if cached_results is not None:
                logger.debug("Cache hit for query: %s...", query[:50])
                return cached_results
        
        # Acquire read lock for safe concurrent access
        with self._lock:
            # Try hybrid search (vector + FTS)
            if self.vector_search_available:
                try:
                    # Phase 2: Hybrid Search - Execute both vector and FTS searches
                    vector_results = self._vector_search_raw(query, filters, limit=20)
                    fts_results = self._fts_search_raw(query, filters, limit=20)
                    
                    # Phase 2, Task 2.3: Reciprocal Rank Fusion
                    fused_results = self._reciprocal_rank_fusion(vector_results, fts_results, k=60)
                    
                    # Phase 2, Task 2.4: Optional Cross-Encoder Re-Ranking
                    # Re-rank top N results for final accuracy boost (10-15% improvement)
                    if self._is_reranking_enabled():
                        fused_results = self._rerank(query, fused_results, top_n=10)
                    
                    # Take top n after fusion (and optional re-ranking)
                    results = fused_results[:n]
                    
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    # Update relevance scores with elapsed time as metadata
                    for result in results:
                        result.metadata["query_time_ms"] = elapsed_ms
                        result.metadata["search_method"] = "hybrid"
                    
                    # Cache results
                    if self.cache_enabled:
                        self._cache_result(cache_key, results)
                    
                    logger.info(
                        "Hybrid search completed: %s vector + %s FTS results in %.1fms",
                        len(vector_results),
                        len(fts_results),
                        elapsed_ms
                    )
                    return results
                
                except Exception as e:
                    logger.error("Hybrid search failed: %s", e, exc_info=True)
                    logger.info("Falling back to grep search")
            
            # Grep fallback
            results = self._grep_fallback(query, n)
            elapsed_ms = (time.time() - start_time) * 1000
            
            for result in results:
                result.metadata["query_time_ms"] = elapsed_ms
            
            logger.info(
                "Grep search completed: %s results in %.1fms",
                len(results),
                elapsed_ms
            )
            return results
    
    def _vector_search_raw(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int = 20
    ) -> List[SearchResult]:
        """Execute vector similarity search using LanceDB.
        
        Part of hybrid search (Phase 2, Task 2.2). Returns raw vector search
        results for fusion with FTS results.
        
        Args:
            query: Natural language search query
            filters: Optional metadata filters (phase, framework_type, tags, is_critical)
            limit: Maximum number of results to return (default: 20 for fusion)
        
        Returns:
            List of SearchResult objects sorted by vector similarity.
            Empty list if no matches found or table unavailable.
        
        Raises:
            RuntimeError: If embedding model or table unavailable
        
        Example:
            >>> results = index._vector_search_raw(
            ...     query="testing standards",
            ...     filters={"phase": 1},
            ...     limit=20
            ... )
        """
        if self.table is None:
            raise RuntimeError("LanceDB table not available")
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Build search query
        search_query = self.table.search(query_embedding).limit(limit)
        
        # Apply metadata filters using WHERE clause (Phase 3, Task 3.4)
        where_clause = self._build_where_clause(filters)
        if where_clause:
            search_query = search_query.where(where_clause)
        
        # Execute search
        raw_results = search_query.to_list()
        
        # Convert to SearchResult objects
        return self._convert_lance_results(raw_results, "vector")
    
    def _fts_search_raw(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        limit: int = 20
    ) -> List[SearchResult]:
        """Execute Full-Text Search (FTS/BM25) using LanceDB.
        
        Part of hybrid search (Phase 2, Task 2.2). Returns raw FTS search
        results for fusion with vector results.
        
        Uses LanceDB's native FTS index with BM25 scoring for keyword-based
        search. Complements vector search by catching exact phrase matches.
        
        Args:
            query: Search query (keywords or phrases)
            filters: Optional metadata filters (same as vector search)
            limit: Maximum number of results to return (default: 20 for fusion)
        
        Returns:
            List of SearchResult objects sorted by BM25 relevance.
            Empty list if no matches found or FTS unavailable.
        
        Raises:
            RuntimeError: If table unavailable
        
        Example:
            >>> results = index._fts_search_raw(
            ...     query="production code checklist",
            ...     filters={"domain": "testing"},
            ...     limit=20
            ... )
        
        Note:
            FTS search is gracefully skipped if FTS index doesn't exist.
            System logs warning and returns empty list.
        """
        if self.table is None:
            raise RuntimeError("LanceDB table not available")
        
        try:
            # LanceDB FTS API: table.search(text_query)
            # No MATCH operator needed - search() with string automatically uses FTS index
            search_query = self.table.search(query)
            
            # Apply metadata filters if provided (Phase 3, Task 3.5)
            where_clause = self._build_where_clause(filters)
            if where_clause:
                search_query = search_query.where(where_clause)
            
            # Execute FTS search
            raw_results = search_query.limit(limit).to_list()
            
            # Convert to SearchResult objects
            return self._convert_lance_results(raw_results, "fts")
        
        except Exception as e:
            # FTS might not be available (index creation failed)
            # This is non-fatal - hybrid search continues with vector-only
            logger.warning("FTS search failed: %s. Continuing with vector-only.", e)
            return []
    
    def _convert_lance_results(
        self,
        raw_results: list,
        search_method: str
    ) -> List[SearchResult]:
        """Convert LanceDB raw results to SearchResult objects.
        
        Shared helper for vector and FTS search result conversion.
        
        Args:
            raw_results: Raw results from LanceDB query
            search_method: "vector" or "fts" (for metadata tracking)
        
        Returns:
            List of SearchResult objects with standardized format
        """
        results = []
        for result in raw_results:
            try:
                # Calculate relevance score based on search method
                if search_method == "vector":
                    # LanceDB vector search returns _distance (lower is better)
                    distance = result.get("_distance", 1.0)
                    relevance_score = 1.0 / (1.0 + distance)
                else:  # fts
                    # LanceDB FTS returns _score (BM25, higher is better)
                    # Normalize to 0-1 range
                    bm25_score = result.get("_score", 0.0)
                    relevance_score = min(1.0, bm25_score / 10.0)  # Simple normalization
                
                # Extract metadata
                metadata = {
                    "phase": result.get("phase", 0),
                    "framework_type": result.get("framework_type", ""),
                    "is_critical": result.get("is_critical", False),
                    "token_count": result.get("token_count", 0),
                    "section_header": result.get("section_header", ""),
                    "search_method": search_method,
                }
                
                # Parse JSON fields safely
                try:
                    if "tags" in result:
                        tags_value = result["tags"]
                        if isinstance(tags_value, str):
                            metadata["tags"] = json.loads(tags_value)
                        elif isinstance(tags_value, list):
                            metadata["tags"] = tags_value
                        else:
                            metadata["tags"] = []
                except (json.JSONDecodeError, TypeError):
                    metadata["tags"] = []
                
                results.append(SearchResult(
                    content=result["content"],
                    file_path=result["file_path"],
                    relevance_score=relevance_score,
                    content_type="standards",
                    metadata=metadata,
                    chunk_id=result.get("chunk_id"),
                    line_range=None
                ))
            except (KeyError, TypeError) as e:
                logger.warning("Failed to convert result: %s", e)
                continue
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        list1: List[SearchResult],
        list2: List[SearchResult],
        k: int = 60
    ) -> List[SearchResult]:
        """Combine two ranked lists using Reciprocal Rank Fusion (RRF).
        
        RRF is a proven algorithm for merging results from different retrieval
        methods (vector + keyword). Items appearing in both lists receive
        higher scores due to additive scoring.
        
        Formula: RRF_score(item) = sum(1 / (k + rank_i)) for all lists
        
        Args:
            list1: First ranked list (typically vector search results)
            list2: Second ranked list (typically FTS search results)
            k: Constant for RRF formula (default: 60, standard from research)
        
        Returns:
            Merged list sorted by RRF score descending. Items in both lists
            rank higher than items in only one list.
        
        Example:
            >>> vector_results = [chunk1, chunk2, chunk3]
            >>> fts_results = [chunk2, chunk3, chunk4]
            >>> fused = index._reciprocal_rank_fusion(vector_results, fts_results)
            >>> # chunk2 and chunk3 rank highest (appear in both)
        
        Note:
            k=60 is the standard value from RRF research papers. Lower k gives
            more weight to top-ranked items, higher k makes ranking more uniform.
        """
        # Track RRF scores by chunk_id (unique identifier)
        # Items appearing in both lists get additive scores
        rrf_scores: Dict[str, float] = {}
        item_map: Dict[str, SearchResult] = {}
        
        # Score items from list 1 (vector search)
        for rank, item in enumerate(list1, start=1):
            chunk_id = item.chunk_id or f"{item.file_path}:{item.content[:50]}"
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))
            item_map[chunk_id] = item  # Store for retrieval
        
        # Score items from list 2 (FTS search)
        for rank, item in enumerate(list2, start=1):
            chunk_id = item.chunk_id or f"{item.file_path}:{item.content[:50]}"
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))
            if chunk_id not in item_map:
                item_map[chunk_id] = item  # Only store if not already present
        
        # Sort by RRF score descending
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Build result list with updated relevance scores
        fused_results = []
        for chunk_id, rrf_score in sorted_items:
            result = item_map[chunk_id]
            # Create new SearchResult with RRF score as relevance
            fused_result = SearchResult(
                content=result.content,
                file_path=result.file_path,
                relevance_score=rrf_score,  # RRF score replaces original score
                content_type=result.content_type,
                metadata={
                    **result.metadata,
                    "fusion_method": "reciprocal_rank_fusion",
                    "original_score": result.relevance_score,
                },
                chunk_id=result.chunk_id,
                line_range=result.line_range
            )
            fused_results.append(fused_result)
        
        logger.debug(
            "RRF fusion: %s vector + %s FTS → %s unique items",
            len(list1),
            len(list2),
            len(fused_results)
        )
        
        return fused_results
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> Optional[str]:
        """Build SQL WHERE clause from filters dict for metadata pre-filtering.
        
        Phase 3, Task 3.3: Converts filter dictionary to LanceDB SQL WHERE clause.
        This enables efficient pre-filtering using scalar indexes before vector search.
        
        Args:
            filters: Dictionary of metadata filters. Supported keys:
                - phase: int (0-8)
                - is_critical: bool
                - framework_type: str (domain)
                - tags: List[str]
        
        Returns:
            SQL WHERE clause string, or None if no filters provided.
            Examples:
                {"phase": 1} → "phase = 1"
                {"phase": 1, "is_critical": True} → "phase = 1 AND is_critical = True"
                {} → None
        
        Note:
            Uses AND logic between different filter types.
            Tags use LIKE for substring matching.
            SQL injection prevention: integer/boolean filters validated by type.
        
        Example:
            >>> clause = index._build_where_clause({"phase": 1, "is_critical": True})
            >>> # Returns: "phase = 1 AND is_critical = True"
        """
        if not filters:
            return None
        
        where_conditions = []
        
        # Phase filter (int, 0-8)
        if "phase" in filters:
            phase = filters["phase"]
            if isinstance(phase, int):
                where_conditions.append(f"phase = {phase}")
        
        # Critical flag filter (bool)
        if "is_critical" in filters:
            is_critical = filters["is_critical"]
            if isinstance(is_critical, bool):
                where_conditions.append(f"is_critical = {is_critical}")
        
        # Framework type / domain filter (string)
        if "framework_type" in filters:
            framework_type = filters["framework_type"]
            if isinstance(framework_type, str):
                # Escape single quotes for SQL safety
                safe_framework = framework_type.replace("'", "''")
                where_conditions.append(f"framework_type = '{safe_framework}'")
        
        # Tags filter (list of strings, OR logic within tags)
        if "tags" in filters and isinstance(filters["tags"], list):
            for tag in filters["tags"]:
                if isinstance(tag, str):
                    # Escape single quotes and use LIKE for substring match
                    safe_tag = tag.replace("'", "''")
                    where_conditions.append(f"tags LIKE '%{safe_tag}%'")
        
        # Return AND-joined conditions, or None if no valid conditions
        return " AND ".join(where_conditions) if where_conditions else None
    
    def _is_reranking_enabled(self) -> bool:
        """Check if cross-encoder re-ranking is enabled in config.
        
        Returns:
            True if reranking is enabled in config, False otherwise.
            Defaults to False if config section not present.
        """
        try:
            return self.config.get("retrieval", {}).get("rerank", {}).get("enabled", False)
        except (KeyError, AttributeError):
            return False
    
    def _rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_n: int = 10
    ) -> List[SearchResult]:
        """Re-rank top N results using cross-encoder for final accuracy boost.
        
        Cross-encoders provide 10-15% accuracy improvement over bi-encoders by
        jointly encoding query+document pairs. However, they are computationally
        expensive, so we only re-rank the top N results after RRF fusion.
        
        Args:
            query: Original search query
            results: Fused results from hybrid search (RRF output)
            top_n: Number of top results to re-rank (default: 10)
        
        Returns:
            Re-ranked results with top N re-ordered by cross-encoder scores.
            Results beyond top N are appended in original order.
        
        Raises:
            ImportError: If sentence-transformers CrossEncoder not available
            RuntimeError: If cross-encoder model fails to load
        
        Example:
            >>> fused_results = self._reciprocal_rank_fusion(vec, fts)
            >>> reranked = self._rerank("testing standards", fused_results, top_n=10)
            >>> # Top 10 results now ordered by cross-encoder relevance
        
        Note:
            Default model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
            Model loads lazily on first re-rank call and is cached.
            Only re-ranks if len(results) >= 2, otherwise returns as-is.
        """
        # Skip re-ranking if too few results
        if len(results) < 2:
            return results
        
        try:
            # Lazy import of CrossEncoder (expensive dependency)
            from sentence_transformers import CrossEncoder
            
            # Get model name from config or use default
            model_name = self.config.get("retrieval", {}).get("rerank", {}).get(
                "model", "cross-encoder/ms-marco-MiniLM-L-6-v2"
            )
            
            # Load cross-encoder model (will cache on first call)
            # Note: This is a simplified implementation. Production would cache the model
            # as an instance variable to avoid reloading on every search.
            logger.debug("Loading cross-encoder model: %s", model_name)
            cross_encoder = CrossEncoder(model_name)
            
            # Create (query, document) pairs for top N results
            top_results = results[:top_n]
            pairs = [(query, r.content) for r in top_results]
            
            # Score all pairs (returns numpy array of scores)
            logger.debug("Re-ranking top %d results with cross-encoder", len(pairs))
            scores = cross_encoder.predict(pairs)
            
            # Zip results with scores and sort by score descending
            scored_results = list(zip(top_results, scores))
            scored_results.sort(key=lambda x: float(x[1]), reverse=True)
            
            # Build final result list with updated relevance scores
            reranked_results = []
            for result, score in scored_results:
                # Create new SearchResult with cross-encoder score
                reranked = SearchResult(
                    content=result.content,
                    file_path=result.file_path,
                    relevance_score=float(score),  # Cross-encoder score
                    content_type=result.content_type,
                    metadata={
                        **result.metadata,
                        "rerank_method": "cross_encoder",
                        "pre_rerank_score": result.relevance_score,
                    },
                    chunk_id=result.chunk_id,
                    line_range=result.line_range
                )
                reranked_results.append(reranked)
            
            # Append remaining results (not re-ranked)
            final_results = reranked_results + results[top_n:]
            
            logger.debug(
                "Re-ranking complete: %d results re-ordered by cross-encoder",
                len(reranked_results)
            )
            
            return final_results
            
        except ImportError as e:
            logger.warning(
                "CrossEncoder not available (sentence-transformers): %s. "
                "Skipping re-ranking.",
                e
            )
            return results
        except Exception as e:
            logger.error(
                "Cross-encoder re-ranking failed: %s. Returning original results.",
                e
            )
            return results
    
    def _vector_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        n: int
    ) -> List[SearchResult]:
        """Perform vector similarity search with LanceDB.
        
        Args:
            query: Search query
            filters: Metadata filters
            n: Number of results
        
        Returns:
            List of SearchResult objects
        
        Raises:
            RuntimeError: If table not available
        """
        if self.table is None:
            raise RuntimeError("LanceDB table not available for vector search")
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Build LanceDB query
        search_query = self.table.search(query_embedding).limit(n * 2)
        
        # Apply filters using WHERE clauses (uses shared builder)
        where_clause = self._build_where_clause(filters)
        if where_clause:
            search_query = search_query.where(where_clause)
        
        # Execute search
        raw_results = search_query.to_list()
        
        # Convert to SearchResult objects
        results = []
        for result in raw_results[:n]:
            try:
                # LanceDB returns distance (lower is better)
                # Convert to similarity score (0-1 range, higher is better)
                distance = result.get("_distance", 1.0)
                relevance_score = 1.0 / (1.0 + distance)
                
                # Extract metadata
                metadata = {
                    "phase": result.get("phase", 0),
                    "framework_type": result.get("framework_type", ""),
                    "is_critical": result.get("is_critical", False),
                    "token_count": result.get("token_count", 0),
                    "section_header": result.get("section_header", ""),
                }
                
                # Parse JSON fields safely
                try:
                    if "tags" in result:
                        metadata["tags"] = json.loads(result["tags"])
                except (json.JSONDecodeError, TypeError):
                    metadata["tags"] = []
                
                results.append(SearchResult(
                    content=result["content"],
                    file_path=result["file_path"],
                    relevance_score=relevance_score,
                    content_type="standards",
                    metadata=metadata,
                    chunk_id=result.get("chunk_id", ""),
                    line_range=None  # Not tracked in current schema
                ))
            
            except Exception as e:
                logger.warning("Failed to parse result: %s", e)
                continue
        
        return results
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for query text.
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector as list of floats
        
        Raises:
            RuntimeError: If embedding generation fails
        """
        if self.embedding_provider == "local":
            if self.local_model is None:
                raise RuntimeError("Local embedding model not initialized")
            embedding = self.local_model.encode(text, convert_to_numpy=True)
            return cast(List[float], embedding.tolist())
        
        if self.embedding_provider == "openai":
            import openai
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding  # type: ignore[no-any-return]
        
        raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")
    
    def _grep_fallback(self, query: str, n: int) -> List[SearchResult]:
        """Fallback to grep-based search when vector search unavailable.
        
        Args:
            query: Search query
            n: Number of results
        
        Returns:
            List of SearchResult objects from grep matches
        """
        logger.info("Using grep fallback for query: %s...", query[:50])
        
        # Get source paths from config
        source_paths = self.config.get("source_paths", [".praxis-os/standards"])
        if not source_paths:
            logger.warning("No source_paths configured for grep fallback")
            return []
        
        # Use first source path for grep
        search_path = Path(source_paths[0])
        if not search_path.exists():
            logger.warning("Search path does not exist: %s", search_path)
            return []
        
        try:
            # Extract search terms (simple word splitting)
            search_terms = query.lower().split()[:3]  # Limit to 3 terms
            
            results = []
            seen_files = set()
            
            for term in search_terms:
                try:
                    result = subprocess.run(
                        [
                            "grep",
                            "-r",
                            "-i",
                            "-l",  # Files with matches
                            "-m", "1",  # Stop after first match
                            term,
                            str(search_path),
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    
                    # Parse matched files
                    for line in result.stdout.splitlines():
                        if line and line not in seen_files:
                            seen_files.add(line)
                            
                            # Read file content (preview)
                            try:
                                content = Path(line).read_text(encoding="utf-8")[:1000]
                                results.append(SearchResult(
                                    content=content,
                                    file_path=line,
                                    relevance_score=0.5,  # Grep match score
                                    content_type="standards",
                                    metadata={"grep_term": term},
                                    chunk_id="grep_match",
                                    line_range=None
                                ))
                            except Exception as e:
                                logger.debug("Could not read %s: %s", line, e)
                        
                        if len(results) >= n:
                            break
                    
                    if len(results) >= n:
                        break
                
                except subprocess.TimeoutExpired:
                    logger.warning("Grep search timed out for term: %s", term)
                    continue
            
            return results[:n]
        
        except Exception as e:
            logger.error("Grep fallback failed: %s", e)
            return []
    
    def update(self, changed_files: List[str]) -> None:
        """Update index for changed files (incremental update).
        
        Args:
            changed_files: List of file paths that have changed
        
        Raises:
            NotImplementedError: Incremental update not yet implemented
        
        Note:
            This will be implemented in Phase 6 (File Watcher Integration).
            For now, use build(force=True) to rebuild entire index.
        """
        raise NotImplementedError(
            "Incremental update not yet implemented. "
            "Use build(force=True) to rebuild entire index."
        )
    
    def delete(self, file_paths: List[str]) -> None:
        """Delete specified files from index.
        
        Args:
            file_paths: List of file paths to remove from index
        
        Raises:
            NotImplementedError: Delete not yet implemented
        
        Note:
            This will be implemented in Phase 6 (File Watcher Integration).
            For now, use build(force=True) to rebuild entire index.
        """
        raise NotImplementedError(
            "Delete not yet implemented. "
            "Use build(force=True) to rebuild entire index."
        )
    
    def reload_index(self) -> None:
        """Reload LanceDB index for hot reload after rebuild.
        
        Reconnects to LanceDB and reopens the table. Clears query cache to
        ensure fresh results. Blocks all search operations until complete.
        
        Thread Safety:
            Uses write lock to prevent concurrent queries during reload.
            Sets _rebuilding event to signal queries to wait.
        
        Example:
            >>> # After file watcher detects changes and rebuilds index
            >>> index.reload_index()  # Picks up new content immediately
        """
        with self._lock:
            self._rebuilding.set()
            try:
                logger.info("Reloading LanceDB index...")
                
                # Close old connections
                if hasattr(self, "table"):
                    del self.table
                if hasattr(self, "db"):
                    del self.db
                
                # Reconnect
                self.db = lancedb.connect(str(self.cache_path))
                self.table = self.db.open_table("praxis_os_standards")
                chunk_count = self.table.count_rows()
                logger.info("Index reloaded: %s chunks", chunk_count)
                self.vector_search_available = True
                
                # Clear cache
                self._query_cache.clear()
            
            except Exception as e:
                logger.error("Failed to reload index: %s", e)
                self.vector_search_available = False
            finally:
                self._rebuilding.clear()
    
    def _generate_cache_key(
        self,
        query: str,
        filters: Optional[Dict[str, Any]],
        n: int
    ) -> str:
        """Generate cache key from query parameters.
        
        Args:
            query: Search query
            filters: Metadata filters
            n: Number of results
        
        Returns:
            MD5 hash as cache key
        """
        key_data = f"{query}:{n}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[List[SearchResult]]:
        """Check if cached result exists and is fresh.
        
        Args:
            cache_key: Cache key to look up
        
        Returns:
            Cached results if fresh, None otherwise
        """
        with self._lock:
            if cache_key not in self._query_cache:
                return None
            
            results, timestamp = self._query_cache[cache_key]
            
            # Check if expired
            if time.time() - timestamp > self.cache_ttl_seconds:
                del self._query_cache[cache_key]
                return None
            
            return results
    
    def _cache_result(
        self,
        cache_key: str,
        results: List[SearchResult]
    ) -> None:
        """Cache search results with timestamp.
        
        Args:
            cache_key: Cache key for storage
            results: Search results to cache
        """
        self._query_cache[cache_key] = (results, time.time())
        
        # Clean old cache entries if cache is large
        if len(self._query_cache) > 100:
            self._clean_cache()
    
    def _clean_cache(self) -> None:
        """Remove expired cache entries (thread-safe)."""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key
                for key, (_, timestamp) in list(self._query_cache.items())
                if current_time - timestamp > self.cache_ttl_seconds
            ]
            for key in expired_keys:
                del self._query_cache[key]
    
    def __del__(self):
        """Clean up resources, including file lock."""
        if hasattr(self, '_lock_file') and self._lock_file:
            try:
                self._lock_file.close()
                logger.debug("Released shared lock on index")
            except Exception as e:
                logger.warning("Failed to release lock: %s", e)

