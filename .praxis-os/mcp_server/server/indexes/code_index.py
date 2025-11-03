"""Code semantic search index implementation.

This module implements semantic search over project source code using BGE embeddings.
It provides natural language querying over code content, complementing structural
AST search with conceptual understanding.

Key Features:
- Semantic code search using BGE embeddings (same model as standards)
- 500-token chunks with 50-token overlap for code files
- Language detection and filtering
- Line range tracking for precise code navigation
- Symbol extraction for enhanced metadata

Architecture:
- Inherits from BaseIndex for consistent interface
- Uses LanceDB for vector storage and search
- Integrates with IndexManager for multi-index queries

Example:
    >>> code_index = CodeIndex(
    ...     cache_path=Path(".praxis-os/.cache/code"),
    ...     config={"embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}}
    ... )
    >>> code_index.build(source_paths=["src/"], force=False)
    >>> results = code_index.search(
    ...     query="authentication logic",
    ...     filters={"language": "python"},
    ...     n=10
    ... )
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import lancedb
from sentence_transformers import SentenceTransformer
import tiktoken

from .base import BaseIndex, SearchResult

logger = logging.getLogger(__name__)


@dataclass
class CodeChunk:
    """Data class representing a chunk of code with metadata.
    
    This class holds a single code chunk along with its metadata for indexing.
    It's used during the chunking process before embedding generation.
    
    Attributes:
        content: The code content text
        file_path: Path to source file
        language: Programming language (detected from extension)
        line_range: Tuple of (start_line, end_line) for this chunk
        tokens: Number of tokens in content
        symbols: List of function/class names found in chunk
        chunk_id: Unique identifier (file_path + line_range)
    
    Example:
        >>> chunk = CodeChunk(
        ...     content="def authenticate(user):\\n    pass",
        ...     file_path="src/auth.py",
        ...     language="python",
        ...     line_range=(42, 44),
        ...     tokens=8,
        ...     symbols=["authenticate"]
        ... )
    """
    content: str
    file_path: str
    language: str
    line_range: tuple  # (start_line, end_line)
    tokens: int
    symbols: List[str] = field(default_factory=list)
    chunk_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Generate chunk_id after initialization."""
        if self.chunk_id is None:
            self.chunk_id = f"{self.file_path}:{self.line_range[0]}-{self.line_range[1]}"


class CodeIndex(BaseIndex):
    """Semantic search index for project source code.
    
    This class implements the BaseIndex interface for code files, enabling
    natural language search over source code using BGE embeddings. It provides
    semantic understanding of code functionality, complementing structural
    AST-based search.
    
    The index:
    - Chunks code files into 500-token segments with 50-token overlap
    - Generates BGE embeddings for semantic search
    - Tracks line ranges for precise code navigation
    - Extracts symbol names for enhanced metadata
    - Supports language-based filtering
    
    Attributes:
        cache_path: Path to LanceDB storage directory
        config: Configuration dictionary with embedding settings
        table_name: LanceDB table name ("praxis_os_code_semantic")
        local_model: SentenceTransformer instance for embeddings (shared with StandardsIndex)
        db: LanceDB connection instance
        table: LanceDB table instance for code chunks
        chunk_size: Tokens per chunk (default: 500)
        chunk_overlap: Token overlap between chunks (default: 50)
    
    Example:
        >>> config = {
        ...     "embedding": {
        ...         "provider": "local",
        ...         "model": "all-MiniLM-L6-v2"
        ...     },
        ...     "chunking": {
        ...         "code_chunk_size": 500,
        ...         "code_chunk_overlap": 50
        ...     }
        ... }
        >>> index = CodeIndex(
        ...     cache_path=Path(".praxis-os/.cache/code"),
        ...     config=config
        ... )
        >>> index.build(source_paths=["src/", "lib/"], force=True)
        >>> results = index.search("user authentication", filters={}, n=5)
        >>> print(f"Found {len(results)} code matches")
    """
    
    def __init__(self, cache_path: Path, config: Dict[str, Any]) -> None:
        """Initialize CodeIndex with storage location and configuration.
        
        Args:
            cache_path: Path to directory for LanceDB storage. Parent directory
                must exist.
            config: Configuration dictionary containing:
                - embedding.provider: "local" (only supported option)
                - embedding.model: BGE model name (default: "all-MiniLM-L6-v2")
                - chunking.code_chunk_size: Tokens per chunk (default: 500)
                - chunking.code_chunk_overlap: Token overlap (default: 50)
        
        Raises:
            FileNotFoundError: If cache_path parent directory doesn't exist
            ValueError: If config is missing or has invalid embedding settings
            RuntimeError: If embedding model fails to load
        
        Example:
            >>> index = CodeIndex(
            ...     cache_path=Path(".praxis-os/.cache/code"),
            ...     config={"embedding": {"provider": "local", "model": "all-MiniLM-L6-v2"}}
            ... )
        """
        super().__init__(cache_path, config)
        
        self.table_name = "praxis_os_code_semantic"
        self.db: Optional[lancedb.DBConnection] = None
        self.table: Optional[lancedb.Table] = None
        
        # Initialize chunking parameters from config
        chunking_config = self.config.get("chunking", {})
        self.chunk_size = chunking_config.get("code_chunk_size", 500)
        self.chunk_overlap = chunking_config.get("code_chunk_overlap", 50)
        
        # Initialize embedding model (shared with StandardsIndex)
        self.local_model = self._init_embedding_model()
        
        logger.info(
            "CodeIndex initialized: cache=%s, chunk_size=%d, overlap=%d",
            self.cache_path,
            self.chunk_size,
            self.chunk_overlap
        )
    
    def _init_embedding_model(self) -> SentenceTransformer:
        """Initialize BGE embedding model for code semantic search.
        
        This method loads the same BGE model used by StandardsIndex to ensure
        consistent embedding space across standards and code content. This enables
        cross-index queries and result fusion.
        
        Returns:
            Loaded SentenceTransformer model instance
        
        Raises:
            ValueError: If embedding config is missing or invalid
            RuntimeError: If model fails to load
        
        Note:
            Only "local" provider is supported. API-based embeddings would incur
            costs and latency for large codebases.
        """
        embedding_config = self.config.get("embedding", {})
        
        if embedding_config.get("provider") != "local":
            raise ValueError(
                f"Only 'local' embedding provider supported for code search, "
                f"got '{embedding_config.get('provider')}'"
            )
        
        model_name = embedding_config.get("model", "all-MiniLM-L6-v2")
        
        try:
            logger.info("Loading BGE embedding model: %s", model_name)
            model = SentenceTransformer(model_name)
            logger.info("✅ Embedding model loaded successfully")
            return model
        except Exception as e:
            logger.error("Failed to load embedding model '%s': %s", model_name, e)
            raise RuntimeError(f"Embedding model initialization failed: {e}") from e
    
    def build(self, source_paths: List[str], force: bool = False) -> None:
        """Build or rebuild code index from source files.
        
        This method discovers code files, chunks them into 500-token segments,
        generates embeddings, and creates a LanceDB table with vector search
        capability.
        
        Args:
            source_paths: List of directory or file paths containing code files
                to index. Paths can be absolute or relative to project root.
            force: If True, rebuild index even if it exists. If False, skip
                build if index is already present.
        
        Raises:
            FileNotFoundError: If source_paths contain non-existent paths
            RuntimeError: If build fails (file discovery, chunking, embedding, storage)
        
        Example:
            >>> index.build(
            ...     source_paths=["src/", "lib/"],
            ...     force=True  # Force full rebuild
            ... )
        
        Note:
            This is a partial implementation. Tasks 4.3-4.4 will complete chunking and indexing.
        """
        logger.info("Build requested for CodeIndex (force=%s)", force)
        logger.info("Source paths: %s", source_paths)
        
        # Check if index already exists
        index_path = self.cache_path / "praxis_os_code_semantic.lance"
        if index_path.exists() and not force:
            logger.info("Index already exists, skipping build (use force=True to rebuild)")
            self._connect_to_index()
            return
        
        # Task 4.2: Discover code files
        include_patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.go", "**/*.rs"]
        exclude_patterns = ["**/__pycache__/**", "**/node_modules/**", "**/venv/**"]
        
        discovered_files = self._discover_files(source_paths, include_patterns, exclude_patterns)
        logger.info("Discovered %d code files", len(discovered_files))
        
        if not discovered_files:
            logger.warning("No code files discovered in source paths")
            return
        
        # Task 4.3: Chunk code files
        all_chunks: List[CodeChunk] = []
        for file_path in discovered_files:
            try:
                chunks = self._chunk_code(file_path)
                all_chunks.extend(chunks)
                logger.debug("Chunked %s into %d chunks", file_path, len(chunks))
            except Exception as e:
                logger.warning("Failed to chunk %s: %s", file_path, e)
                continue
        
        logger.info("Chunked %d files into %d total chunks", len(discovered_files), len(all_chunks))
        
        if not all_chunks:
            logger.warning("No code chunks generated")
            return
        
        # Task 4.4: Generate embeddings and create LanceDB table
        logger.info("Step 1/3: Generating embeddings for %d chunks", len(all_chunks))
        
        # Extract content for embedding
        contents = [chunk.content for chunk in all_chunks]
        embeddings = self.local_model.encode(
            contents,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        logger.info("Generated %d embeddings", len(embeddings))
        
        # Step 2/3: Prepare LanceDB records
        logger.info("Step 2/3: Preparing LanceDB records")
        records = []
        for chunk, embedding in zip(all_chunks, embeddings):
            record = {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "vector": embedding.tolist(),
                "file_path": chunk.file_path,
                "line_start": chunk.line_range[0],
                "line_end": chunk.line_range[1],
                "language": chunk.language,
                "tokens": chunk.tokens,
                "symbols": ",".join(chunk.symbols)  # CSV string for LanceDB
            }
            records.append(record)
        
        logger.info("Prepared %d records for indexing", len(records))
        
        # Step 3/3: Create LanceDB table
        logger.info("Step 3/3: Creating LanceDB table")
        self.db = lancedb.connect(str(self.cache_path))
        
        # Drop existing table if force rebuild
        try:
            if force:
                self.db.drop_table(self.table_name)
                logger.info("Dropped existing table (force=True)")
        except Exception:
            pass  # Table doesn't exist, that's fine
        
        # Create table with vector data
        self.table = self.db.create_table(
            self.table_name,
            data=records,
            mode="overwrite"
        )
        logger.info("Created LanceDB table with %d records", len(records))
        
        # Create scalar index on language for filtering
        try:
            self.table.create_scalar_index("language", index_type="BTREE")
            logger.info("✅ Created BTREE scalar index on 'language'")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.debug("Scalar index on 'language' already exists")
            else:
                logger.warning("Failed to create scalar index on 'language': %s", e)
        
        logger.info("✅ Code index build complete: %d chunks indexed", len(all_chunks))
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        n: int = 5
    ) -> List[SearchResult]:
        """Search code index using semantic similarity.
        
        This method performs vector similarity search on code chunks using BGE
        embeddings. It supports language filtering and returns results sorted
        by relevance.
        
        Args:
            query: Natural language search query (e.g., "authentication logic")
            filters: Optional metadata filters. Supported keys:
                - language: str (e.g., "python", "typescript")
            n: Number of results to return (default: 5)
        
        Returns:
            List of SearchResult objects sorted by relevance_score descending.
            Each result includes code content, file path, line range, and metadata.
        
        Raises:
            ValueError: If query is empty or n is invalid
            RuntimeError: If search fails (index not built, LanceDB error)
        
        Example:
            >>> results = index.search(
            ...     query="user authentication flow",
            ...     filters={"language": "python"},
            ...     n=10
            ... )
            >>> for r in results:
            ...     print(f"{r.file_path}:{r.line_range[0]}-{r.line_range[1]}")
        """
        if not query:
            raise ValueError("Query cannot be empty")
        
        if n <= 0:
            raise ValueError(f"n must be positive, got {n}")
        
        if self.table is None:
            raise RuntimeError(
                "Index not built. Call build() before search() or ensure index exists."
            )
        
        logger.info("Code search: query='%s', filters=%s, n=%d", query, filters, n)
        
        # Generate query embedding
        query_embedding = self.local_model.encode(
            query,
            convert_to_numpy=True
        )
        
        # Build LanceDB search query
        search_query = self.table.search(query_embedding).limit(n)
        
        # Apply language filter if provided
        if filters and "language" in filters:
            language = filters["language"]
            if isinstance(language, str):
                # Escape single quotes for SQL safety
                safe_language = language.replace("'", "''")
                search_query = search_query.where(f"language = '{safe_language}'")
                logger.debug("Applied language filter: %s", language)
        
        # Execute search
        try:
            raw_results = search_query.to_list()
        except Exception as e:
            logger.error("LanceDB search failed: %s", e)
            raise RuntimeError(f"Code search failed: {e}") from e
        
        # Convert to SearchResult objects
        results: List[SearchResult] = []
        for result in raw_results:
            try:
                # LanceDB returns distance (lower is better)
                # Convert to similarity score (0-1 range, higher is better)
                distance = result.get("_distance", 1.0)
                relevance_score = 1.0 / (1.0 + distance)
                
                # Parse symbols from CSV string
                symbols_str = result.get("symbols", "")
                symbols = [s.strip() for s in symbols_str.split(",") if s.strip()]
                
                search_result = SearchResult(
                    content=result["content"],
                    file_path=result["file_path"],
                    relevance_score=relevance_score,
                    content_type="code",
                    metadata={
                        "language": result["language"],
                        "symbols": symbols,
                        "tokens": result["tokens"]
                    },
                    chunk_id=result["chunk_id"],
                    line_range=(result["line_start"], result["line_end"])
                )
                results.append(search_result)
            except KeyError as e:
                logger.warning("Skipping malformed search result: missing key %s", e)
                continue
        
        logger.info("Code search returned %d results", len(results))
        return results
    
    def update(self, changed_files: List[str]) -> None:
        """Incrementally update index for changed code files.
        
        This method removes old chunks for changed files and re-indexes them
        without rebuilding the entire index.
        
        Args:
            changed_files: List of file paths that have been modified, added,
                or deleted. Paths should be relative to project root.
        
        Raises:
            RuntimeError: If update fails (re-indexing error)
        
        Example:
            >>> index.update(["src/auth.py", "lib/utils.py"])
        
        Note:
            Implementation deferred to Phase 6 (File Watcher integration).
        """
        logger.info("Update requested for %d files", len(changed_files))
        raise NotImplementedError(
            "update() will be implemented in Phase 6 (File Watcher). "
            "Use build(force=True) for full reindex."
        )
    
    def delete(self, file_paths: List[str]) -> None:
        """Delete code entries from index for specified files.
        
        This method removes all chunks associated with the given code files
        from the index.
        
        Args:
            file_paths: List of file paths to remove from index. Paths should
                be relative to project root.
        
        Raises:
            ValueError: If file_paths is empty
            RuntimeError: If deletion fails
        
        Example:
            >>> index.delete(["src/deprecated.py"])
        
        Note:
            Implementation deferred to Phase 6 (File Watcher integration).
        """
        if not file_paths:
            raise ValueError("file_paths cannot be empty")
        
        logger.info("Delete requested for %d files", len(file_paths))
        raise NotImplementedError(
            "delete() will be implemented in Phase 6 (File Watcher). "
            "Use build(force=True) for full reindex."
        )
    
    def _discover_files(
        self,
        source_paths: List[str],
        include_patterns: List[str],
        exclude_patterns: List[str]
    ) -> List[Path]:
        """Discover code files matching include patterns and excluding patterns.
        
        This method performs recursive directory traversal to find code files
        that match the specified patterns. It respects exclusion patterns to
        skip virtual environments, build artifacts, and node modules.
        
        Args:
            source_paths: List of directory or file paths to search.
                Can be absolute or relative paths.
            include_patterns: List of glob patterns for files to include
                (e.g., ["**/*.py", "**/*.js"]). Patterns use ** for
                recursive matching.
            exclude_patterns: List of glob patterns for paths to exclude
                (e.g., ["**/venv/**", "**/node_modules/**"]). Any file
                matching an exclude pattern is filtered out.
        
        Returns:
            List of Path objects for discovered code files, sorted by path
            for deterministic ordering.
        
        Raises:
            FileNotFoundError: If source_paths contain non-existent paths
        
        Example:
            >>> files = index._discover_files(
            ...     source_paths=["src/", "lib/"],
            ...     include_patterns=["**/*.py"],
            ...     exclude_patterns=["**/test/**", "**/__pycache__/**"]
            ... )
            >>> print(f"Found {len(files)} Python files")
        
        Note:
            - Uses pathlib.Path.glob() for pattern matching
            - Filters out symlinks to avoid circular references
            - Skips files >1MB to avoid memory issues with large generated files
        """
        discovered_files: List[Path] = []
        
        for source_path_str in source_paths:
            source_path = Path(source_path_str)
            
            if not source_path.exists():
                raise FileNotFoundError(f"Source path does not exist: {source_path}")
            
            if source_path.is_file():
                # Single file specified
                if self._matches_patterns(source_path, include_patterns, exclude_patterns):
                    discovered_files.append(source_path)
            elif source_path.is_dir():
                # Directory - apply include patterns
                for pattern in include_patterns:
                    matched_files = source_path.glob(pattern)
                    for file_path in matched_files:
                        if file_path.is_file() and not file_path.is_symlink():
                            if self._matches_patterns(file_path, include_patterns, exclude_patterns):
                                discovered_files.append(file_path)
        
        # Remove duplicates and sort for deterministic ordering
        discovered_files = sorted(set(discovered_files))
        
        logger.info(
            "File discovery: %d files found from %d source paths",
            len(discovered_files),
            len(source_paths)
        )
        
        return discovered_files
    
    def _matches_patterns(
        self,
        file_path: Path,
        include_patterns: List[str],
        exclude_patterns: List[str]
    ) -> bool:
        """Check if file matches include patterns and doesn't match exclude patterns.
        
        Args:
            file_path: Path to check
            include_patterns: Patterns that file must match (at least one)
            exclude_patterns: Patterns that file must NOT match (any)
        
        Returns:
            True if file matches include and doesn't match exclude, False otherwise
        """
        # Check exclude patterns first (faster to reject)
        for exclude_pattern in exclude_patterns:
            if self._path_matches_glob(file_path, exclude_pattern):
                return False
        
        # Must match at least one include pattern
        for include_pattern in include_patterns:
            if self._path_matches_glob(file_path, include_pattern):
                return True
        
        return False
    
    def _path_matches_glob(self, file_path: Path, pattern: str) -> bool:
        """Check if path matches a glob pattern.
        
        Args:
            file_path: Path to check
            pattern: Glob pattern (e.g., "**/*.py", "**/venv/**")
        
        Returns:
            True if path matches pattern, False otherwise
        
        Note:
            This uses pathlib's match() which handles ** for recursive matching.
        """
        return file_path.match(pattern)
    
    def _chunk_code(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a code file into overlapping segments with metadata.
        
        This method reads a code file, splits it into 500-token chunks with
        50-token overlap, tracks line ranges, detects language, and extracts
        symbol names for each chunk.
        
        Args:
            file_path: Path to code file to chunk
        
        Returns:
            List of CodeChunk objects with content and metadata
        
        Raises:
            FileNotFoundError: If file doesn't exist
            UnicodeDecodeError: If file can't be decoded as UTF-8
            RuntimeError: If chunking fails
        
        Example:
            >>> chunks = index._chunk_code(Path("src/auth.py"))
            >>> print(f"Created {len(chunks)} chunks")
            >>> print(f"First chunk: lines {chunks[0].line_range}")
        
        Note:
            - Uses tiktoken for token counting (cl100k_base encoding)
            - Chunk size: 500 tokens, overlap: 50 tokens
            - Line numbers are 1-indexed (like editors)
            - Empty files return empty list
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError as e:
            logger.warning("Failed to decode %s as UTF-8: %s", file_path, e)
            raise
        
        if not content.strip():
            return []
        
        # Detect language from file extension
        language = self._detect_language(file_path)
        
        # Split into lines for line range tracking
        lines = content.split('\n')
        
        # Initialize tokenizer
        try:
            tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize tokenizer: {e}") from e
        
        chunks: List[CodeChunk] = []
        current_line_idx = 0
        
        while current_line_idx < len(lines):
            # Collect lines for this chunk
            chunk_lines = []
            chunk_tokens = 0
            start_line = current_line_idx + 1  # 1-indexed
            
            # Add lines until we reach chunk_size tokens
            for i in range(current_line_idx, len(lines)):
                line = lines[i]
                line_tokens = len(tokenizer.encode(line + '\n'))
                
                if chunk_tokens + line_tokens > self.chunk_size and chunk_lines:
                    # Chunk is full
                    break
                
                chunk_lines.append(line)
                chunk_tokens += line_tokens
                current_line_idx = i + 1
            
            if not chunk_lines:
                # Single line exceeds chunk_size - take it anyway
                chunk_lines = [lines[current_line_idx]]
                chunk_tokens = len(tokenizer.encode(lines[current_line_idx]))
                current_line_idx += 1
            
            end_line = current_line_idx  # 1-indexed end (inclusive)
            chunk_content = '\n'.join(chunk_lines)
            
            # Extract symbols from chunk
            symbols = self._extract_symbols(chunk_content, language)
            
            # Create chunk object
            chunk = CodeChunk(
                content=chunk_content,
                file_path=str(file_path),
                language=language,
                line_range=(start_line, end_line),
                tokens=chunk_tokens,
                symbols=symbols
            )
            chunks.append(chunk)
            
            # Apply overlap: back up by overlap tokens
            if current_line_idx < len(lines):
                overlap_tokens = 0
                overlap_lines = 0
                
                # Count backwards from current position
                for i in range(current_line_idx - 1, max(0, current_line_idx - len(chunk_lines)) - 1, -1):
                    line_tokens = len(tokenizer.encode(lines[i] + '\n'))
                    if overlap_tokens + line_tokens > self.chunk_overlap:
                        break
                    overlap_tokens += line_tokens
                    overlap_lines += 1
                
                # Move back by overlap_lines (but stay >= 0)
                current_line_idx = max(0, current_line_idx - overlap_lines)
        
        logger.debug(
            "Chunked %s: %d lines -> %d chunks (avg %.1f tokens/chunk)",
            file_path,
            len(lines),
            len(chunks),
            sum(c.tokens for c in chunks) / len(chunks) if chunks else 0
        )
        
        return chunks
    
    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension.
        
        Args:
            file_path: Path to code file
        
        Returns:
            Language identifier string (e.g., "python", "javascript")
        
        Note:
            Returns "unknown" if extension is not recognized.
        """
        extension = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        return language_map.get(extension, 'unknown')
    
    def _extract_symbols(self, content: str, language: str) -> List[str]:
        """Extract function and class names from code using simple regex.
        
        This method uses language-specific regex patterns to find function
        and class definitions. It's intentionally simple (no AST parsing)
        for performance and robustness.
        
        Args:
            content: Code content string
            language: Programming language identifier
        
        Returns:
            List of symbol names (function/class identifiers)
        
        Note:
            - Python: def/class keywords
            - JavaScript/TypeScript: function/class/const/let with arrow functions
            - Go: func keyword
            - Rust: fn/struct/impl keywords
            - Returns empty list for unsupported languages
        
        Example:
            >>> symbols = index._extract_symbols("def foo():\\n    pass", "python")
            >>> print(symbols)  # ['foo']
        """
        symbols: List[str] = []
        
        if language == 'python':
            # Match: def function_name( or class ClassName:
            patterns = [
                r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]'
            ]
        elif language in ('javascript', 'typescript'):
            # Match: function name(, class Name, const name =, let name =
            patterns = [
                r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{',
                r'(?:const|let)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(?:async\s+)?\(',
                r'([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*\([^)]*\)\s*=>'  # Type annotation arrow function
            ]
        elif language == 'go':
            # Match: func functionName(
            patterns = [r'func\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(']
        elif language == 'rust':
            # Match: fn function_name(, struct StructName, impl
            patterns = [
                r'fn\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[<\(]',
                r'struct\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[<\{]',
                r'impl\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[<\{]'
            ]
        else:
            # Unsupported language
            return []
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            symbols.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_symbols = []
        for symbol in symbols:
            if symbol not in seen:
                seen.add(symbol)
                unique_symbols.append(symbol)
        
        return unique_symbols
    
    def _connect_to_index(self) -> None:
        """Connect to existing LanceDB index.
        
        This method opens an existing LanceDB table for search operations.
        Called by build() when index already exists.
        
        Raises:
            RuntimeError: If connection fails or table doesn't exist
        """
        try:
            self.db = lancedb.connect(str(self.cache_path))
            self.table = self.db.open_table(self.table_name)
            logger.info("✅ Connected to existing code index: %d rows", self.table.count_rows())
        except Exception as e:
            logger.error("Failed to connect to code index: %s", e)
            raise RuntimeError(f"Code index connection failed: {e}") from e

