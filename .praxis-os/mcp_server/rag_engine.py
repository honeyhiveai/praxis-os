"""
prAxIs OS RAG Engine - LanceDB Implementation
Semantic search with metadata filtering and fallback mechanisms.

Switched from ChromaDB to LanceDB for:
- Built-in WHERE clause filtering (fast!)
- No singleton client conflicts (clean hot reload)
- Simpler reconnection logic

100% AI-authored via human orchestration.
"""

# pylint: disable=too-many-instance-attributes
# Justification: RAGEngine requires 12 attributes to manage vector DB connection,
# embedding models, caching, and configuration - all essential state

# pylint: disable=too-many-arguments,too-many-positional-arguments
# Justification: __init__ needs 6 parameters for flexible configuration of
# database path, embedding provider, model, dimension, cache, and LLM fallback

# pylint: disable=import-outside-toplevel
# Justification: Heavy ML dependencies (sentence-transformers, openai) loaded
# lazily only when needed to reduce startup time and support optional features

# pylint: disable=broad-exception-caught
# Justification: RAG engine catches broad exceptions for robustness - vector
# search failures fall back to grep, ensuring service availability

# pylint: disable=too-many-locals
# Justification: Complex search logic with filtering, ranking, and fallback
# requires multiple intermediate variables for clarity

import fcntl
import hashlib
import json
import logging
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import lancedb

from .models.rag import SearchResult
from .server.indexes.index_manager import IndexManager
from .server.indexes.standards_index import StandardsIndex

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Semantic search engine for prAxIs OS standards.
    
    REFACTORED: Delegates to IndexManager instead of creating duplicate StandardsIndex.

    Features:
    - Delegates to IndexManager's StandardsIndex (uses correct config)
    - Grep fallback for offline/error scenarios
    - Legacy query caching (for backward compatibility)
    """

    def __init__(
        self,
        standards_path: Path,
        index_manager: Optional[Any] = None,
        cache_ttl_seconds: int = 3600,
    ):
        """
        Initialize RAG engine with IndexManager delegation.

        Args:
            standards_path: Path to prAxIs OS standards for grep fallback
            index_manager: IndexManager instance (provides StandardsIndex)
            cache_ttl_seconds: Cache time-to-live in seconds (default: 1 hour)
        """
        self.standards_path = standards_path
        self.cache_ttl_seconds = cache_ttl_seconds
        self.index_manager = index_manager

        # Query cache and lock for backward compatibility and thread safety
        # NOTE: StandardsIndex has its own cache, but we keep this for
        # legacy callers and as a second-level cache
        self._query_cache: Dict[str, tuple] = {}
        self._lock = threading.RLock()

        # Get StandardsIndex from IndexManager (no duplicate creation!)
        if self.index_manager:
            try:
                logger.info("Initializing RAG engine with IndexManager delegation")
                self.standards_index = self.index_manager.get_index("standards")
                self.vector_search_available = self.standards_index is not None
                if self.vector_search_available:
                    logger.info("✅ RAG engine using IndexManager's StandardsIndex")
                else:
                    logger.warning("⚠️  StandardsIndex not available, grep fallback only")
            except Exception as e:
                logger.warning("Failed to get StandardsIndex from IndexManager: %s", e)
                logger.warning("Vector search unavailable, grep fallback will be used")
                self.vector_search_available = False
                self.standards_index = None
        else:
            logger.warning("No IndexManager provided to RAGEngine, grep fallback only")
            self.vector_search_available = False
            self.standards_index = None

    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict] = None,
    ) -> SearchResult:
        """
        Search prAxIs OS standards with intelligent retrieval.

        This method now delegates to StandardsIndex for vector search while
        maintaining backward compatibility with the existing API.

        Steps:
        1. Check cache for recent identical query
        2. Delegate to StandardsIndex.search()
        3. Convert new SearchResult format to legacy format
        4. Return structured results

        If vector search fails, falls back to grep.

        Args:
            query: Search query text
            n_results: Number of results to return (default: 5)
            filters: Optional metadata filters:
                - phase: int (phase number to filter by)
                - tags: List[str] (tags to filter by)
                - framework: str (framework type to filter by)
                - is_critical: bool (only critical content)

        Returns:
            SearchResult with chunks, metadata, and metrics (legacy format)

        Example:
            # Get Phase 1 requirements
            result = engine.search(
                "Phase 1 method verification requirements",
                n_results=5,
                filters={"phase": 1}
            )
        """
        start_time = time.time()

        # Check cache
        cache_key = self._generate_cache_key(query, n_results, filters)
        cached_result = self._check_cache(cache_key)
        if cached_result:
            logger.debug("Cache hit for query: %s...", query[:50])
            return cached_result

        # Try delegating to StandardsIndex
        if self.vector_search_available and self.standards_index:
            try:
                # Delegate to new architecture
                new_results = self.standards_index.search(
                    query=query,
                    filters=filters,
                    n=n_results
                )
                
                # Convert to legacy format
                result = self._convert_to_legacy_format(new_results)
                elapsed_ms = (time.time() - start_time) * 1000
                result.query_time_ms = elapsed_ms

                # Cache result
                self._cache_result(cache_key, result)

                logger.info(
                    "Vector search completed: %s chunks in %.1fms",
                    len(result.chunks),
                    elapsed_ms,
                )
                return result

            except Exception as e:
                logger.error("StandardsIndex search failed: %s", e, exc_info=True)
                logger.info("Falling back to grep search")

        # Grep fallback
        result = self._grep_fallback(query, n_results)
        elapsed_ms = (time.time() - start_time) * 1000
        result.query_time_ms = elapsed_ms

        logger.info(
            "Grep search completed: %s chunks in %.1fms",
            len(result.chunks),
            elapsed_ms,
        )
        return result

    def _convert_to_legacy_format(
        self,
        new_results: List[Any]
    ) -> SearchResult:
        """Convert new SearchResult format to legacy format.
        
        Args:
            new_results: List of SearchResult objects from StandardsIndex
        
        Returns:
            SearchResult in legacy format (with chunks list)
        """
        chunks = []
        relevance_scores = []
        total_tokens = 0
        
        for result in new_results:
            # Convert each new SearchResult to legacy chunk format
            chunk = {
                "content": result.content,
                "file_path": result.file_path,
                "section_header": result.metadata.get("section_header", ""),
                "parent_headers": result.metadata.get("parent_headers", []),
                "token_count": result.metadata.get("token_count", 0),
                "phase": result.metadata.get("phase", 0),
                "framework_type": result.metadata.get("framework_type", ""),
                "category": result.metadata.get("category", ""),
                "is_critical": result.metadata.get("is_critical", False),
                "tags": result.metadata.get("tags", []),
            }
            chunks.append(chunk)
            relevance_scores.append(result.relevance_score)
            total_tokens += chunk["token_count"]
        
        return SearchResult(
            chunks=chunks,
            total_tokens=total_tokens,
            retrieval_method="vector",
            query_time_ms=0.0,  # Will be set by caller
            relevance_scores=relevance_scores,
            cache_hit=False
        )
    
    def _vector_search(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> SearchResult:
        """
        Perform vector similarity search with LanceDB.

        Args:
            query: Search query
            n_results: Number of results
            filters: Metadata filters

        Returns:
            SearchResult with vector-retrieved chunks
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Build LanceDB query - table is guaranteed to be available here
        if self.table is None:
            raise RuntimeError("LanceDB table not available for vector search")
        search_query = self.table.search(query_embedding).limit(n_results * 2)

        # Apply filters using WHERE clauses (LanceDB's killer feature!)
        if filters:
            where_conditions = []

            if "phase" in filters:
                where_conditions.append(f"phase = {filters['phase']}")

            if "is_critical" in filters:
                where_conditions.append(f"is_critical = {filters['is_critical']}")

            if "framework" in filters:
                where_conditions.append(f"framework_type = '{filters['framework']}'")

            if "tags" in filters:
                # Tags are JSON array, need to check if any match
                for tag in filters["tags"]:
                    where_conditions.append(f"tags LIKE '%{tag}%'")

            # Combine conditions with AND
            if where_conditions:
                where_clause = " AND ".join(where_conditions)
                search_query = search_query.where(where_clause)

        # Execute search
        results = search_query.to_list()

        # Convert to chunks format
        chunks = []
        scores = []
        total_tokens = 0

        for result in results[:n_results]:
            # Parse JSON fields
            try:
                parent_headers = json.loads(result.get("parent_headers", "[]"))
                tags = json.loads(result.get("tags", "[]"))
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                logger.debug("Failed to parse metadata fields: %s", e)
                parent_headers = []
                tags = []

            chunk = {
                "content": result["content"],
                "file_path": result["file_path"],
                "section_header": result["section_header"],
                "parent_headers": parent_headers,
                "token_count": result["token_count"],
                "phase": result["phase"],
                "framework_type": result["framework_type"],
                "category": result.get("category", ""),
                "is_critical": result["is_critical"],
                "tags": tags,
            }

            chunks.append(chunk)
            scores.append(result.get("_distance", 0.0))  # LanceDB returns distance
            total_tokens += result["token_count"]

        return SearchResult(
            chunks=chunks,
            total_tokens=total_tokens,
            retrieval_method="vector",
            query_time_ms=0.0,  # Set by caller
            relevance_scores=scores,
            cache_hit=False,
        )

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for query text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        if self.embedding_provider == "local":
            if self.local_model is None:
                raise RuntimeError("Local embedding model not initialized")
            embedding = self.local_model.encode(text, convert_to_numpy=True)
            return cast(List[float], embedding.tolist())

        if self.embedding_provider == "openai":
            import openai

            response = openai.embeddings.create(model=self.embedding_model, input=text)
            # OpenAI SDK returns embedding as list[float] but type-stubbed as Any
            return response.data[0].embedding  # type: ignore[no-any-return]

        raise ValueError(f"Unknown embedding provider: {self.embedding_provider}")

    def _grep_fallback(self, query: str, n_results: int) -> SearchResult:
        """
        Fallback to grep-based search when vector search unavailable.

        Args:
            query: Search query
            n_results: Number of results

        Returns:
            SearchResult with grep-retrieved chunks
        """
        logger.info("Using grep fallback for query: %s...", query[:50])

        try:
            # Extract search terms (simple word splitting)
            search_terms = query.lower().split()

            # Run grep for each term
            chunks = []
            seen_files = set()

            for term in search_terms[:3]:  # Limit to 3 most important terms
                result = subprocess.run(
                    [
                        "grep",
                        "-r",
                        "-i",
                        "-l",  # Files with matches
                        "-m",
                        "1",  # Stop after first match per file
                        term,
                        str(self.standards_path),
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

                        # Read file content (up to first 1000 chars)
                        try:
                            content = Path(line).read_text(encoding="utf-8")[:1000]
                            chunks.append(
                                {
                                    "content": content,
                                    "file_path": line,
                                    "section_header": "Grep Match",
                                    "token_count": len(content.split()),
                                }
                            )
                        except Exception as e:
                            logger.debug("Could not read %s: %s", line, e)

                    if len(chunks) >= n_results:
                        break

                if len(chunks) >= n_results:
                    break

            total_tokens = sum(
                int(c["token_count"]) if isinstance(c["token_count"], (int, str)) else 0
                for c in chunks
            )

            return SearchResult(
                chunks=chunks[:n_results],
                total_tokens=total_tokens,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[1.0] * len(chunks),
                cache_hit=False,
            )

        except Exception as e:
            logger.error("Grep fallback failed: %s", e)
            return SearchResult(
                chunks=[],
                total_tokens=0,
                retrieval_method="grep_fallback",
                query_time_ms=0.0,
                relevance_scores=[],
                cache_hit=False,
            )

    def _generate_cache_key(
        self, query: str, n_results: int, filters: Optional[Dict]
    ) -> str:
        """Generate cache key from query parameters.

        Creates MD5 hash of query, n_results, and filters for cache lookup.

        :param query: Search query text
        :type query: str
        :param n_results: Number of results requested
        :type n_results: int
        :param filters: Optional metadata filters
        :type filters: Optional[Dict]
        :return: MD5 hash as cache key
        :rtype: str
        """
        key_data = f"{query}:{n_results}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[SearchResult]:
        """Check if cached result exists and is fresh (thread-safe).

        Lock must be held for all cache operations to prevent race conditions
        where multiple threads check/modify cache simultaneously.

        Returns cached result if found and not expired, otherwise None.

        Thread Safety:
        - Acquires lock before checking cache
        - Prevents concurrent modification during read/delete
        - Safe for concurrent search operations

        :param cache_key: Cache key to look up
        :type cache_key: str
        :return: Cached search result if fresh, None otherwise
        :rtype: Optional[SearchResult]
        """
        # Lock must be held for all cache operations
        with self._lock:
            if cache_key not in self._query_cache:
                return None

            result: SearchResult
            result, timestamp = self._query_cache[cache_key]

            # Check if expired
            if time.time() - timestamp > self.cache_ttl_seconds:
                del self._query_cache[cache_key]
                return None

            # Return cached result with cache_hit flag
            result.cache_hit = True
            return result

    def _cache_result(self, cache_key: str, result: SearchResult) -> None:
        """Cache search result with timestamp.

        Stores result in cache and triggers cleanup if cache grows too large.

        :param cache_key: Cache key for storage
        :type cache_key: str
        :param result: Search result to cache
        :type result: SearchResult
        """
        self._query_cache[cache_key] = (result, time.time())

        # Clean old cache entries if cache is large
        if len(self._query_cache) > 100:
            self._clean_cache()

    def _clean_cache(self) -> None:
        """Remove expired cache entries (thread-safe).

        Iterates through cache and deletes entries that have exceeded
        the TTL threshold.

        Thread Safety:
        - Uses list() copy to prevent RuntimeError during iteration
        - Safe to call concurrently with cache reads/writes
        - Lock held during entire operation

        Note:
            Must be called while holding self._lock (if called externally)
            or will acquire lock if called directly.
        """
        # Lock must be held for all cache operations
        with self._lock:
            current_time = time.time()
            # Use list() to create snapshot - prevents RuntimeError if cache modified
            expired_keys = [
                key
                for key, (_, timestamp) in list(self._query_cache.items())
                if current_time - timestamp > self.cache_ttl_seconds
            ]
            for key in expired_keys:
                del self._query_cache[key]

    def health_check(self) -> Dict[str, Any]:
        """
        Check RAG engine health status.

        Returns:
            Health status dictionary
        """
        health = {
            "vector_search_available": self.vector_search_available,
            "index_path": str(self.index_path),
            "standards_path": str(self.standards_path),
            "embedding_provider": self.embedding_provider,
        }

        if self.vector_search_available and self.standards_index:
            try:
                if self.standards_index.table is not None:
                    health["chunk_count"] = self.standards_index.table.count_rows()
                    health["status"] = "healthy"
                else:
                    health["status"] = "degraded"
                    health["error"] = "Table not initialized"
            except Exception as e:
                health["status"] = "degraded"
                health["error"] = str(e)
        else:
            health["status"] = "grep_only"

        return health

    def reload_index(self) -> None:
        """Reload LanceDB index for hot reload after rebuild.

        Delegates to StandardsIndex for index reload. Clears RAGEngine's
        query cache to ensure fresh results.

        **Thread Safety:**

        StandardsIndex handles its own locking. RAGEngine clears its cache
        after delegate completes.

        **Example:**

        .. code-block:: python

            # After editing prAxIs OS content
            rag_engine.reload_index()  # Picks up new content immediately

        **Note:**

        This is typically called automatically by the file watcher when
        prAxIs OS content changes are detected.
        """
        logger.info("Reloading index...")
        
        if self.standards_index:
            try:
                # Delegate to StandardsIndex
                self.standards_index.reload_index()
                
                # Clear RAGEngine's cache
                self._query_cache.clear()
                
                logger.info("Index reload complete")
            except Exception as e:
                logger.error("Failed to reload index: %s", e)
                self.vector_search_available = False
        else:
            logger.warning("No StandardsIndex to reload")
