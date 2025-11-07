"""Code index container - orchestrates semantic and graph implementations.

This is the main interface for code index operations. It implements BaseIndex
and orchestrates two internal implementations: SemanticIndex (LanceDB) and 
GraphIndex (DuckDB).

Architecture:
    CodeIndex (container)
        ├── SemanticIndex (LanceDB: vector + FTS + scalar search)
        └── GraphIndex (DuckDB: AST + call graph + recursive CTEs)

The container provides:
    - BaseIndex interface compliance
    - Lock management during build/update (prevents concurrent corruption)
    - Semantic search via LanceDB (code embeddings)
    - Structural search via DuckDB (AST patterns)
    - Graph traversal via DuckDB (find_callers, find_dependencies, find_call_paths)
    - Aggregated health checks and statistics

Classes:
    CodeIndex: Container implementing BaseIndex

Design Pattern: Facade / Orchestration
- CodeIndex is the public API
- SemanticIndex and GraphIndex are internal implementations
- Container delegates operations to appropriate sub-index
- Extended methods (search_ast, find_callers, etc.) provide graph capabilities

Traceability:
    - Task 2.4: Create CodeIndex container with dual-database orchestration
    - FR-001: Uniform container entry point
    - FR-007: Internal implementation hidden
    - FR-003: File locking for corruption prevention
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import CodeIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.code.graph import GraphIndex
from ouroboros.subsystems.rag.code.semantic import SemanticIndex
from ouroboros.subsystems.rag.lock_manager import IndexLockManager
from ouroboros.subsystems.rag.utils.corruption_detector import is_corruption_error
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class CodeIndex(BaseIndex):
    """Code index container - orchestrates semantic and graph implementations.
    
    Implements BaseIndex interface and orchestrates two internal indexes:
    1. SemanticIndex (LanceDB): Semantic code search using CodeBERT embeddings
    2. GraphIndex (DuckDB): AST + call graph analysis with recursive CTEs
    
    Design:
    - Dual-database orchestration (LanceDB for semantic, DuckDB for structural)
    - Lock management for build/update (prevents concurrent corruption)
    - Semantic search delegates to SemanticIndex
    - Structural/graph queries delegate to GraphIndex
    - Aggregated health checks and statistics
    
    Usage:
        >>> from ouroboros.config.mcp_config import MCPConfig
        >>> config = MCPConfig().rag.code
        >>> base_path = Path("/tmp/praxis-os")
        >>> index = CodeIndex(config, base_path)
        >>> 
        >>> # Build both indexes
        >>> index.build(source_paths=[Path("ouroboros/")])
        >>> 
        >>> # Semantic search
        >>> results = index.search("error handling patterns")
        >>> 
        >>> # Structural search
        >>> ast_results = index.search_ast("async_function")
        >>> 
        >>> # Graph traversal
        >>> callers = index.find_callers("process_request", max_depth=3)
        >>> dependencies = index.find_dependencies("main", max_depth=5)
        >>> paths = index.find_call_paths("main", "database_query", max_depth=10)
    """
    
    def __init__(self, config: CodeIndexConfig, base_path: Path) -> None:
        """Initialize code index container.
        
        Args:
            config: CodeIndexConfig from MCPConfig
            base_path: Base directory for index storage
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Create internal indexes
        self._semantic_index = SemanticIndex(config, base_path)
        self._graph_index = GraphIndex(config.graph, base_path, languages=config.languages)
        
        # Create lock manager for concurrency control
        lock_dir = base_path / ".cache" / "locks"
        self._lock_manager = IndexLockManager("code", lock_dir)
        
        logger.info("CodeIndex container initialized (semantic + graph) with lock management")
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build code index (both semantic and graph) from source paths.
        
        Acquires exclusive lock before building to prevent concurrent corruption.
        Builds both indexes in sequence:
        1. SemanticIndex: LanceDB vector + FTS + scalar (for semantic search)
        2. GraphIndex: DuckDB AST + call graph (for structural/graph queries)
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if indexes exist
            
        Raises:
            ActionableError: If build fails or lock cannot be acquired
        """
        logger.info("CodeIndex.build() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("CodeIndex.build() building semantic index (LanceDB)")
            self._semantic_index.build(source_paths, force)
            
            logger.info("CodeIndex.build() building graph index (DuckDB)")
            self._graph_index.build(source_paths, force)
            
        logger.info("✅ CodeIndex built successfully (semantic + graph)")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search code index using semantic search (CodeBERT embeddings).
        
        Delegates to SemanticIndex for hybrid search (vector + FTS + RRF).
        Acquires shared lock for read access (allows multiple concurrent readers).
        
        For structural queries, use search_ast().
        For graph traversal, use find_callers/find_dependencies/find_call_paths().
        
        Args:
            query: Natural language or code search query
            n_results: Number of results to return
            filters: Optional filters (language, file_path)
            
        Returns:
            List of SearchResult objects with line ranges
            
        Raises:
            IndexError: If search fails (after auto-repair attempt if corrupted)
        """
        with self._lock_manager.shared_lock():
            try:
                return self._semantic_index.search(query, n_results, filters)
            except Exception as e:
                # Check if this is a corruption error
                if is_corruption_error(e):
                    logger.warning("Corruption detected during search, attempting auto-repair...")
                    raise ActionableError(
                        what_failed="Search code index (semantic)",
                        why_failed=f"Index corrupted: {e}",
                        how_to_fix="Auto-repair required. Rebuild semantic index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update code index (both semantic and graph) for changed files.
        
        Acquires exclusive lock before updating to prevent concurrent corruption.
        Updates both indexes:
        1. SemanticIndex: Re-chunks and re-embeds changed files
        2. GraphIndex: Re-extracts AST and relationships for changed files
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails or lock cannot be acquired
        """
        logger.info("CodeIndex.update() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("CodeIndex.update() updating semantic index")
            self._semantic_index.update(changed_files)
            
            logger.info("CodeIndex.update() updating graph index")
            self._graph_index.update(changed_files)
            
        logger.info("✅ CodeIndex updated successfully (semantic + graph)")
    
    def health_check(self) -> HealthStatus:
        """Check code index health (aggregated from semantic + graph).
        
        Checks both sub-indexes and aggregates results:
        - Semantic (LanceDB): Table exists, has chunks, FTS/scalar indexes present
        - Graph (DuckDB): Tables exist, have data (AST nodes, symbols, relationships)
        
        Returns:
            HealthStatus indicating if both indexes are operational
        """
        semantic_health = self._semantic_index.health_check()
        graph_health = self._graph_index.health_check()
        
        # Aggregate health status
        overall_healthy = semantic_health.healthy and graph_health.healthy
        
        if overall_healthy:
            return HealthStatus(
                healthy=True,
                message=f"Code index operational (semantic + graph)",
                details={
                    "semantic": semantic_health.details,
                    "graph": graph_health.details,
                },
                last_updated=None
            )
        else:
            # Determine which component is unhealthy
            issues = []
            if not semantic_health.healthy:
                issues.append(f"semantic: {semantic_health.message}")
            if not graph_health.healthy:
                issues.append(f"graph: {graph_health.message}")
            
            return HealthStatus(
                healthy=False,
                message=f"Code index has issues: {'; '.join(issues)}",
                details={
                    "semantic": semantic_health.details,
                    "graph": graph_health.details,
                },
                last_updated=None
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get code index statistics (aggregated from semantic + graph).
        
        Returns statistics from both sub-indexes:
        - Semantic: chunk_count, embedding_model, languages, fts_enabled
        - Graph: ast_node_count, symbol_count, relationship_count
        
        Returns:
            Dictionary with aggregated statistics
        """
        semantic_stats = self._semantic_index.get_stats()
        graph_stats = self._graph_index.get_stats()
        
        return {
            "semantic": semantic_stats,
            "graph": graph_stats,
            "total_chunks": semantic_stats.get("chunk_count", 0),
            "total_ast_nodes": graph_stats.get("ast_node_count", 0),
            "total_symbols": graph_stats.get("symbol_count", 0),
            "total_relationships": graph_stats.get("relationship_count", 0),
        }
    
    # ========================================================================
    # Extended Methods (not in BaseIndex, specific to code index)
    # ========================================================================
    
    def search_ast(
        self,
        pattern: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search AST index by node type or symbol name (structural search).
        
        Delegates to GraphIndex for AST pattern queries.
        Enables finding code by structure, not semantics.
        
        Examples:
            - search_ast("function_definition") → all functions
            - search_ast("async_function") → all async functions
            - search_ast("error_handler") → error handling code
        
        Args:
            pattern: Node type or symbol name pattern to search
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type)
            
        Returns:
            List of dictionaries with AST node information
            
        Raises:
            IndexError: If query fails
        """
        with self._lock_manager.shared_lock():
            return self._graph_index.search_ast(pattern, n_results, filters)
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Delegates to GraphIndex for recursive CTE graph traversal.
        
        Example:
            find_callers("process_request", max_depth=3)
            → Returns: handle_api_call, main, server_loop (chain of callers)
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth (default: 10)
            
        Returns:
            List of caller information with paths
            
        Raises:
            IndexError: If query fails
        """
        with self._lock_manager.shared_lock():
            return self._graph_index.find_callers(symbol_name, max_depth)
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Delegates to GraphIndex for recursive CTE graph traversal.
        
        Example:
            find_dependencies("main", max_depth=3)
            → Returns: init_app, load_config, start_server (chain of calls)
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth (default: 10)
            
        Returns:
            List of dependency information with paths
            
        Raises:
            IndexError: If query fails
        """
        with self._lock_manager.shared_lock():
            return self._graph_index.find_dependencies(symbol_name, max_depth)
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Delegates to GraphIndex for recursive CTE path finding.
        
        Example:
            find_call_paths("main", "database_query", max_depth=5)
            → Returns: [["main", "init_app", "setup_db", "database_query"],
                       ["main", "process_request", "database_query"]]
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length (default: 10)
            
        Returns:
            List of call paths (each path is a list of symbol names)
            
        Raises:
            IndexError: If query fails
        """
        with self._lock_manager.shared_lock():
            return self._graph_index.find_call_paths(from_symbol, to_symbol, max_depth)
