"""Standards index container - delegates to semantic implementation.

This is the main interface for standards index operations. It implements BaseIndex
and delegates all operations to the internal semantic implementation.

Architecture:
    StandardsIndex (container)
        └── SemanticIndex (internal implementation)
            └── LanceDB (vector + FTS + scalar search)

The container provides:
    - BaseIndex interface compliance
    - Delegation to semantic implementation
    - Future: Lock management during build/update
    - Future: Auto-repair on corruption detection

Classes:
    StandardsIndex: Container implementing BaseIndex

Design Pattern: Facade / Delegation
- StandardsIndex is the public API
- SemanticIndex is the internal implementation
- Container delegates all operations to SemanticIndex

Traceability:
    - Task 2.2: Migrate SemanticIndex and implement delegation
    - FR-001: Uniform container entry point
    - FR-007: Internal implementation hidden
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import StandardsIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.lock_manager import IndexLockManager
from ouroboros.subsystems.rag.standards.semantic import SemanticIndex
from ouroboros.subsystems.rag.utils.corruption_detector import is_corruption_error
from ouroboros.utils.errors import ActionableError

logger = logging.getLogger(__name__)


class StandardsIndex(BaseIndex):
    """Standards index container - delegates to semantic implementation.
    
    Implements BaseIndex interface and delegates to internal SemanticIndex
    for LanceDB operations.
    
    Design:
    - Simple delegation pattern (no lock management yet - that's Task 2.3)
    - Future: Will add lock management during build/update operations
    - Future: May add composite search (semantic + keyword + graph)
    
    Usage:
        >>> config = StandardsIndexConfig(...)
        >>> index = StandardsIndex(config, base_path)
        >>> index.build(source_paths=[Path("standards/")])
        >>> results = index.search("How do workflows work?")
    """
    
    def __init__(self, config: StandardsIndexConfig, base_path: Path) -> None:
        """Initialize standards index container.
        
        Args:
            config: StandardsIndexConfig from MCPConfig
            base_path: Base directory for index storage
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Create internal semantic index
        self._semantic_index = SemanticIndex(config, base_path)
        
        # Create lock manager for concurrency control
        lock_dir = base_path / "cache" / "locks"
        self._lock_manager = IndexLockManager("standards", lock_dir)
        
        logger.info("StandardsIndex container initialized with lock management")
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build standards index from source paths.
        
        Acquires exclusive lock before building to prevent concurrent corruption.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            source_paths: Paths to standard directories/files
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.build() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.build() delegating to SemanticIndex")
            return self._semantic_index.build(source_paths, force)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search standards index with auto-repair on corruption.
        
        Acquires shared lock for read access (allows multiple concurrent readers).
        If corruption is detected, automatically triggers index rebuild and retries.
        Delegates to internal SemanticIndex for hybrid search
        (vector + FTS + RRF + optional reranking).
        
        Args:
            query: Natural language search query
            n_results: Number of results to return
            filters: Optional metadata filters (domain, phase, role)
            
        Returns:
            List of SearchResult objects sorted by relevance
            
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
                    # Release shared lock before acquiring exclusive lock for rebuild
                    # (context manager will handle release)
                    raise ActionableError(
                        what_failed="Search standards index",
                        why_failed=f"Index corrupted: {e}",
                        how_to_fix="Auto-repair required. Call rebuild_secondary_indexes() or rebuild index."
                    ) from e
                else:
                    # Not a corruption error, re-raise
                    raise
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update index for changed files.
        
        Acquires exclusive lock before updating to prevent concurrent corruption.
        Delegates to internal SemanticIndex for implementation.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.update() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.update() delegating to SemanticIndex")
            return self._semantic_index.update(changed_files)
    
    def health_check(self) -> HealthStatus:
        """Check index health.
        
        Delegates to internal SemanticIndex for implementation.
        Verifies table exists, has data, and secondary indexes are present.
        
        Returns:
            HealthStatus indicating if index is operational
        """
        return self._semantic_index.health_check()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Delegates to internal SemanticIndex for implementation.
        
        Returns:
            Dictionary with stats like chunk_count, embedding_model, etc.
        """
        return self._semantic_index.get_stats()
    
    # Additional helper method (not in BaseIndex)
    def rebuild_secondary_indexes(self) -> None:
        """Rebuild only the secondary indexes (FTS + scalar) without touching table data.
        
        Acquires exclusive lock before rebuilding to prevent concurrent access.
        Delegates to internal SemanticIndex. This is a convenience method
        not defined in BaseIndex, but useful for recovery scenarios when
        FTS or scalar indexes are corrupted but the table data is intact.
        
        This is much faster than a full rebuild since it doesn't require
        re-chunking files or regenerating embeddings.
        
        Raises:
            IndexError: If rebuild fails or lock cannot be acquired
        """
        logger.info("StandardsIndex.rebuild_secondary_indexes() acquiring exclusive lock")
        with self._lock_manager.exclusive_lock():
            logger.info("StandardsIndex.rebuild_secondary_indexes() delegating to SemanticIndex")
            return self._semantic_index.rebuild_secondary_indexes()
