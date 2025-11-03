"""Base index interface for multi-index RAG architecture.

This module provides the abstract base class and data models for all index
implementations in prAxIs OS. The BaseIndex class defines the contract that
all specific index types (standards, code, AST) must implement.

The architecture supports:
- Polymorphic index management via IndexManager
- Unified SearchResult format across all index types
- Config-driven index initialization
- Extensibility through subclassing

Example:
    >>> class StandardsIndex(BaseIndex):
    ...     def build(self, source_paths, force=False):
    ...         # Implementation
    ...         pass
    ...     def search(self, query, filters, n):
    ...         # Implementation
    ...         return [SearchResult(...)]
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class SearchResult:
    """Unified search result format across all index types.
    
    This data class provides a consistent return format for all index search
    operations, enabling seamless result aggregation and re-ranking across
    multiple index types.
    
    Attributes:
        content: The matched content (chunk text, code snippet, or symbol definition)
        file_path: Source file path relative to project root
        relevance_score: Relevance score from 0.0 (low) to 1.0 (high)
        content_type: Type of content ("standards", "code", "ast")
        metadata: Additional metadata specific to content type (domain, phase,
            role, language, symbol_type, etc.)
        chunk_id: Unique identifier for the chunk (standards/code only)
        line_range: Line range tuple (start_line, end_line) for code/AST
    
    Example:
        >>> result = SearchResult(
        ...     content="def authenticate(user, password):",
        ...     file_path="src/auth.py",
        ...     relevance_score=0.95,
        ...     content_type="code",
        ...     metadata={"language": "python", "symbols": ["authenticate"]},
        ...     line_range=(42, 58)
        ... )
    """
    
    content: str
    file_path: str
    relevance_score: float
    content_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunk_id: Optional[str] = None
    line_range: Optional[tuple] = None
    
    def __post_init__(self) -> None:
        """Validate search result fields after initialization.
        
        Raises:
            ValueError: If relevance_score is not in [0.0, 1.0] range
            ValueError: If content_type is not recognized
            ValueError: If line_range tuple has invalid format
        """
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError(
                f"relevance_score must be in [0.0, 1.0], got {self.relevance_score}"
            )
        
        valid_content_types = {"standards", "code", "ast"}
        if self.content_type not in valid_content_types:
            raise ValueError(
                f"content_type must be one of {valid_content_types}, "
                f"got '{self.content_type}'"
            )
        
        if self.line_range is not None:
            if (
                not isinstance(self.line_range, tuple)
                or len(self.line_range) != 2
                or not all(isinstance(x, int) for x in self.line_range)
                or self.line_range[0] > self.line_range[1]
            ):
                raise ValueError(
                    f"line_range must be (start, end) tuple with start <= end, "
                    f"got {self.line_range}"
                )


class BaseIndex(ABC):
    """Abstract base class for all index implementations.
    
    This class defines the interface that all index types must implement to
    participate in the multi-index RAG architecture. Subclasses handle specific
    content types (standards, code, AST) with specialized indexing and search
    strategies.
    
    The BaseIndex contract ensures:
    - Consistent initialization via config
    - Standardized build/rebuild process
    - Uniform search interface
    - Incremental update capability
    - Clean resource management
    
    Attributes:
        cache_path: Path to index storage location (LanceDB directory)
        config: Configuration dictionary for this index instance
    
    Example Subclass:
        >>> class StandardsIndex(BaseIndex):
        ...     def __init__(self, cache_path: Path, config: dict):
        ...         super().__init__(cache_path, config)
        ...         self.table_name = "praxis_os_standards"
        ...         self.embedding_model = self._init_embedding_model()
        ...     
        ...     def build(self, source_paths: List[str], force: bool = False):
        ...         # Create LanceDB table, chunk documents, generate embeddings
        ...         pass
        ...     
        ...     def search(self, query: str, filters: dict, n: int):
        ...         # Hybrid search (vector + FTS), apply filters, return results
        ...         return [SearchResult(...)]
    """
    
    def __init__(self, cache_path: Path, config: dict) -> None:
        """Initialize index with storage location and configuration.
        
        Args:
            cache_path: Path to directory for index storage (LanceDB database)
            config: Configuration dictionary containing index-specific settings
                (chunking, embedding models, source paths, etc.)
        
        Raises:
            FileNotFoundError: If cache_path parent directory doesn't exist
            ValueError: If config is missing required fields
        """
        if not cache_path.parent.exists():
            raise FileNotFoundError(
                f"Cache directory parent does not exist: {cache_path.parent}"
            )
        
        if not isinstance(config, dict):
            raise ValueError(f"config must be a dictionary, got {type(config)}")
        
        self.cache_path = cache_path
        self.config = config
    
    @abstractmethod
    def build(self, source_paths: List[str], force: bool = False) -> None:
        """Build or rebuild index from source files.
        
        This method is responsible for:
        - Discovering source files matching configured patterns
        - Processing and chunking content appropriately
        - Generating embeddings (if applicable)
        - Creating index structures (vector, FTS, scalar)
        - Persisting index to cache_path
        
        Args:
            source_paths: List of paths to source directories/files to index
            force: If True, rebuild index even if it already exists. If False,
                skip rebuild if index is up-to-date.
        
        Raises:
            FileNotFoundError: If source_paths contain non-existent paths
            PermissionError: If unable to write to cache_path
            RuntimeError: If index build fails (parsing, embedding, storage)
        
        Example:
            >>> index.build(
            ...     source_paths=[".praxis-os/standards"],
            ...     force=True  # Force full rebuild
            ... )
        """
        pass
    
    @abstractmethod
    def search(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        n: int = 5
    ) -> List[SearchResult]:
        """Search index and return top n results.
        
        This method executes the search strategy specific to this index type:
        - Standards: Hybrid search (vector + FTS + metadata filtering)
        - Code: Semantic search on code text
        - AST: Structural search on symbols
        
        Args:
            query: Search query string (natural language or keyword)
            filters: Optional metadata filters as key-value pairs. Exact format
                depends on index type. Examples:
                - Standards: {"domain": "backend", "phase": 0}
                - Code: {"language": "python"}
                - AST: {"symbol_type": "function"}
            n: Number of results to return (default: 5)
        
        Returns:
            List of SearchResult objects, sorted by relevance_score descending.
            May return fewer than n results if not enough matches found.
        
        Raises:
            ValueError: If query is empty or n is invalid
            RuntimeError: If search fails (index not built, query error)
        
        Example:
            >>> results = index.search(
            ...     query="authentication patterns",
            ...     filters={"domain": "backend"},
            ...     n=10
            ... )
            >>> for result in results:
            ...     print(f"{result.file_path}: {result.relevance_score}")
        """
        pass
    
    @abstractmethod
    def update(self, changed_files: List[str]) -> None:
        """Incrementally update index for changed files.
        
        This method provides efficient incremental updates without full rebuild:
        - Remove old chunks/entries for changed files
        - Re-process and re-index changed files only
        - Preserve unchanged index entries
        
        This is called by the file watcher when files change during development.
        
        Args:
            changed_files: List of file paths that have been modified, added,
                or deleted. Paths should be relative to project root.
        
        Raises:
            FileNotFoundError: If changed_files contain paths not in index
            RuntimeError: If update fails (re-indexing error)
        
        Example:
            >>> index.update([
            ...     ".praxis-os/standards/development/new-standard.md",
            ...     "src/auth.py"
            ... ])
        
        Note:
            Implementations should handle file deletions by removing entries
            from the index without raising errors.
        """
        pass
    
    @abstractmethod
    def delete(self, file_paths: List[str]) -> None:
        """Delete entries from index for specified files.
        
        This method removes all index entries associated with the given files.
        Used during file deletions or when files no longer match indexing criteria.
        
        Args:
            file_paths: List of file paths to remove from index. Paths should
                be relative to project root.
        
        Raises:
            ValueError: If file_paths is empty
            RuntimeError: If deletion fails
        
        Example:
            >>> index.delete([
            ...     ".praxis-os/standards/old-standard.md"
            ... ])
        
        Note:
            It is not an error to delete files that don't exist in the index.
            Implementations should silently succeed in this case.
        """
        pass

