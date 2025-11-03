"""Index manager for orchestrating multiple index types.

This module provides the IndexManager class, which serves as the central
orchestration layer for all index types in the multi-index RAG architecture.
The manager handles:
- Config-driven index initialization
- Query routing to appropriate indexes
- Result aggregation and re-ranking
- Index rebuild coordination

The IndexManager enables polymorphic index management through the BaseIndex
interface, allowing new index types to be added through configuration alone.

Example:
    >>> manager = IndexManager(
    ...     base_path=Path(".praxis-os/.cache"),
    ...     config_path=Path(".praxis-os/config/index_config.yaml")
    ... )
    >>> results = manager.search(
    ...     query="authentication patterns",
    ...     content_type="standards",
    ...     filters={"domain": "backend"},
    ...     n_results=5
    ... )
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .base import BaseIndex, SearchResult

logger = logging.getLogger(__name__)


class IndexManager:
    """Config-driven orchestration of multiple index types.
    
    The IndexManager serves as the single entry point for all search operations
    across different content types (standards, code, AST). It handles:
    
    - Loading configuration from YAML file
    - Dynamically discovering and instantiating indexes based on config
    - Routing queries to appropriate indexes
    - Aggregating results from multiple indexes
    - Optional re-ranking across all results
    
    The manager uses the BaseIndex interface to achieve polymorphism, allowing
    different index implementations to be added or removed through configuration
    alone, without code changes.
    
    Attributes:
        base_path: Root path for all index storage (contains cache directories)
        config: Loaded configuration dictionary from index_config.yaml
        indexes: Dictionary mapping content_type to BaseIndex instances
    
    Example:
        >>> config_path = Path(".praxis-os/config/index_config.yaml")
        >>> manager = IndexManager(
        ...     base_path=Path(".praxis-os/.cache"),
        ...     config_path=config_path
        ... )
        >>> 
        >>> # Search standards
        >>> results = manager.search(
        ...     query="how to implement authentication",
        ...     content_type="standards",
        ...     filters={"phase": 0},
        ...     n_results=5
        ... )
        >>> 
        >>> # Rebuild all indexes
        >>> manager.rebuild_all(force=True)
    """
    
    def __init__(
        self,
        base_path: Path,
        config_path: Optional[Path] = None
    ) -> None:
        """Initialize IndexManager with base path and configuration.
        
        Args:
            base_path: Root directory for index storage. Each index type will
                create its own subdirectory (e.g., base_path/standards/).
            config_path: Path to index_config.yaml file. If None, uses default
                location at base_path/../config/index_config.yaml
        
        Raises:
            FileNotFoundError: If config_path doesn't exist
            ValueError: If config is invalid or missing required fields
            RuntimeError: If index initialization fails
        
        Note:
            The manager creates base_path if it doesn't exist.
        """
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        if config_path is None:
            config_path = base_path.parent / "config" / "index_config.yaml"
        
        self.config = self._load_config(config_path)
        
        # Initialize indexes from config
        self.indexes: Dict[str, BaseIndex] = self._init_indexes()
        
        logger.info(
            f"IndexManager initialized with {len(self.indexes)} indexes: "
            f"{list(self.indexes.keys())}"
        )
    
    def _load_config(self, config_path: Path) -> dict:
        """Load and validate configuration from YAML file.
        
        Args:
            config_path: Path to index_config.yaml
        
        Returns:
            Validated configuration dictionary
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid (missing required sections)
            yaml.YAMLError: If YAML parsing fails
        """
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Expected index_config.yaml at this location."
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML config: {e}") from e
        
        if not isinstance(config, dict):
            raise ValueError(
                f"Config must be a dictionary, got {type(config)}"
            )
        
        # Validate required top-level sections
        required_sections = ["indexes", "retrieval"]
        missing = [s for s in required_sections if s not in config]
        if missing:
            raise ValueError(
                f"Config missing required sections: {missing}\n"
                f"Required: {required_sections}"
            )
        
        logger.debug(f"Loaded config from {config_path}")
        return config
    
    def _init_indexes(self) -> Dict[str, BaseIndex]:
        """Initialize all enabled indexes from configuration.
        
        This method dynamically discovers which indexes are enabled in the
        config and instantiates them. The current implementation supports:
        - standards: StandardsIndex (if implemented)
        - code: CodeIndex (if implemented)
        - ast: ASTIndex (if implemented)
        
        Returns:
            Dictionary mapping content_type to BaseIndex instance
        
        Raises:
            RuntimeError: If index initialization fails
        
        Note:
            This is a placeholder implementation. Full implementation will
            import actual index classes (StandardsIndex, CodeIndex, ASTIndex)
            once they exist. For now, returns empty dict.
        """
        indexes = {}
        
        indexes_config = self.config.get("indexes", {})
        
        for content_type, index_config in indexes_config.items():
            if not index_config.get("enabled", False):
                logger.debug(f"Index '{content_type}' disabled in config")
                continue

            # Dynamic index instantiation
            try:
                if content_type == "standards":
                    from .standards_index import StandardsIndex
                    cache_path = self.base_path / "vector_index"  # Use existing path
                    indexes[content_type] = StandardsIndex(
                        cache_path=cache_path,
                        config=index_config
                    )
                    logger.info(f"✅ Initialized StandardsIndex at {cache_path}")
                elif content_type == "code":
                    from .ast_index import ASTIndex
                    cache_path = self.base_path / "ast"
                    indexes[content_type] = ASTIndex(
                        cache_path=cache_path,
                        config=index_config,
                        base_path=self.base_path.parent  # .praxis-os directory
                    )
                    logger.info(f"✅ Initialized ASTIndex (code search) at {cache_path}")
                else:
                    logger.warning(
                        f"Unknown index type '{content_type}' in config, skipping"
                    )
            except ImportError as e:
                logger.warning(
                    f"Failed to import index class for '{content_type}': {e}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to initialize '{content_type}' index: {e}",
                    exc_info=True
                )
        
        return indexes
    
    def _auto_build_indexes(self) -> None:
        """Automatically build all indexes if they don't exist or are stale.
        
        This method is called during server startup to ensure all indexes
        are ready for queries. It checks each index and triggers incremental
        builds as needed.
        
        Note:
            This method uses incremental builds by default, so it only processes
            changed files. Use rebuild_all(force=True) for full rebuilds.
        """
        if not self.indexes:
            logger.warning("No indexes initialized, skipping auto-build")
            return
        
        logger.info("🔨 Auto-build: Checking if indexes need building...")
        
        for content_type, index in self.indexes.items():
            try:
                # Get source paths from index config
                source_paths = index.config.get('source_paths', [])
                if not source_paths:
                    logger.debug(f"  {content_type}: no source_paths configured, skipping")
                    continue
                
                logger.info(f"  {content_type}: building from {source_paths}")
                
                # Trigger incremental build
                index.build(source_paths, force=False, incremental=True)
                
                logger.info(f"  ✅ {content_type} index ready")
                
            except Exception as e:
                logger.error(
                    f"Failed to auto-build '{content_type}' index: {e}",
                    exc_info=True
                )
    
    def search(
        self,
        query: str,
        content_type: str,
        filters: Optional[Dict[str, Any]] = None,
        n_results: int = 5
    ) -> List[SearchResult]:
        """Search specified index and return top n results.
        
        This method routes the query to the appropriate index based on
        content_type, applies any metadata filters, and returns results
        sorted by relevance.
        
        Args:
            query: Search query string (natural language or keywords)
            content_type: Type of content to search ("standards", "code", "ast")
            filters: Optional metadata filters specific to content type.
                Examples:
                - standards: {"domain": "backend", "phase": 0}
                - code: {"language": "python"}
                - ast: {"symbol_type": "function"}
            n_results: Number of results to return (default: 5)
        
        Returns:
            List of SearchResult objects sorted by relevance_score descending.
            May return fewer than n_results if insufficient matches found.
        
        Raises:
            ValueError: If query is empty, content_type is unknown, or n_results < 1
            RuntimeError: If search fails
        
        Example:
            >>> results = manager.search(
            ...     query="authentication security",
            ...     content_type="standards",
            ...     filters={"domain": "backend"},
            ...     n_results=10
            ... )
            >>> for r in results[:3]:
            ...     print(f"{r.relevance_score:.2f}: {r.file_path}")
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        if n_results < 1:
            raise ValueError(f"n_results must be >= 1, got {n_results}")
        
        if content_type not in self.indexes:
            available = list(self.indexes.keys())
            raise ValueError(
                f"Unknown content_type '{content_type}'. "
                f"Available: {available or 'none (no indexes initialized)'}"
            )
        
        logger.debug(
            f"Searching {content_type} for: '{query}' "
            f"(filters={filters}, n={n_results})"
        )
        
        try:
            # Route to appropriate index
            index = self.indexes[content_type]
            results = index.search(
                query=query,
                filters=filters,
                n=n_results * 2  # Request more for re-ranking
            )
            
            # Re-rank if enabled
            if self.config["retrieval"].get("rerank", {}).get("enabled", False):
                results = self._rerank(query, results)
            
            # Return top n results
            return results[:n_results]
        
        except Exception as e:
            logger.error(f"Search failed for {content_type}: {e}")
            raise RuntimeError(f"Search operation failed: {e}") from e
    
    def _rerank(
        self,
        query: str,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """Re-rank search results using cross-encoder model.
        
        This method applies a cross-encoder model to re-order results based on
        query-document relevance. This is more accurate than initial retrieval
        scores but more expensive, so it's only applied to top candidates.
        
        Args:
            query: Original search query
            results: Initial search results to re-rank
        
        Returns:
            Re-ranked results sorted by updated relevance scores
        
        Note:
            This is a placeholder. Full implementation will use sentence-transformers
            cross-encoder model for re-ranking.
        """
        # TODO: Implement cross-encoder re-ranking
        # from sentence_transformers import CrossEncoder
        # model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        # pairs = [(query, r.content) for r in results]
        # scores = model.predict(pairs)
        # for result, score in zip(results, scores):
        #     result.relevance_score = float(score)
        # return sorted(results, key=lambda r: r.relevance_score, reverse=True)
        
        logger.debug("Re-ranking not yet implemented, returning original order")
        return results
    
    def rebuild_all(self, force: bool = False) -> None:
        """Rebuild all indexes from source files.
        
        This method triggers a full rebuild of all enabled indexes. Use this
        when:
        - Initial setup after installation
        - After major changes to source files
        - After config changes that affect indexing
        - Manually via MCP tool for maintenance
        
        Args:
            force: If True, rebuild even if index appears up-to-date.
                If False, indexes may skip rebuild if current.
        
        Raises:
            RuntimeError: If rebuild fails for any index
        
        Example:
            >>> # Force full rebuild of all indexes
            >>> manager.rebuild_all(force=True)
            >>> 
            >>> # Incremental rebuild (skips up-to-date indexes)
            >>> manager.rebuild_all(force=False)
        """
        logger.info(f"Rebuilding all indexes (force={force})")
        
        for content_type, index in self.indexes.items():
            try:
                # Get source paths from config
                index_config = self.config["indexes"][content_type]
                source_paths = index_config.get("source_paths", [])
                
                if not source_paths:
                    logger.warning(
                        f"No source_paths configured for {content_type}, skipping"
                    )
                    continue
                
                logger.info(f"Rebuilding {content_type} index...")
                index.build(source_paths=source_paths, force=force)
                logger.info(f"Successfully rebuilt {content_type} index")
            
            except Exception as e:
                logger.error(f"Failed to rebuild {content_type} index: {e}")
                raise RuntimeError(
                    f"Index rebuild failed for {content_type}: {e}"
                ) from e
        
        logger.info("All indexes rebuilt successfully")
    
    def get_index(self, content_type: str) -> Optional[BaseIndex]:
        """Get index instance for specified content type.
        
        Args:
            content_type: Content type identifier ("standards", "code", "ast")
        
        Returns:
            BaseIndex instance if content_type exists, None otherwise
        
        Example:
            >>> standards_index = manager.get_index("standards")
            >>> if standards_index:
            ...     # Direct access to index for advanced operations
            ...     standards_index.update(["changed_file.md"])
        """
        return self.indexes.get(content_type)
    
    def list_indexes(self) -> List[str]:
        """List all enabled index content types.
        
        Returns:
            List of content type identifiers for enabled indexes
        
        Example:
            >>> manager.list_indexes()
            ['standards', 'code', 'ast']
        """
        return list(self.indexes.keys())

