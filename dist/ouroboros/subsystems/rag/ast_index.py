"""AST Index: Structural code search using tree-sitter ASTs.

This index provides structural queries over code based on syntax, not semantics.
Unlike semantic search (CodeIndex) which understands meaning, AST search finds
patterns based on code structure.

Use Cases:
- "Find all async functions" (syntax pattern)
- "Find all classes implementing interface X" (structural pattern)
- "Find all error handling blocks" (control flow pattern)
- "Find all functions with >5 parameters" (complexity metrics)

Architecture:
- tree-sitter: Fast, incremental parsing for multiple languages
- SQLite: Lightweight storage for AST metadata
- Per-language parsers: Auto-install via tree-sitter-languages
- Query by node type: function_definition, class_definition, etc.

Mission: Enable "pattern-based discovery" - find code by structure, not content.
"""

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ouroboros.config.schemas.indexes import ASTIndexConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.utils.errors import ActionableError, IndexError

logger = logging.getLogger(__name__)


class ASTIndex(BaseIndex):
    """Structural code search index using tree-sitter.
    
    Provides syntax-based queries over code ASTs:
    - Find by node type (function, class, async_function, etc.)
    - Find by language (Python, TypeScript, etc.)
    - Find by structural patterns
    
    Schema (SQLite):
    - ast_nodes: id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id
    
    Uses tree-sitter for fast, incremental parsing with automatic parser installation.
    """
    
    def __init__(self, config: ASTIndexConfig, base_path: Path):
        """Initialize AST Index.
        
        Args:
            config: ASTIndexConfig from MCPConfig
            base_path: Base path for resolving relative paths
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Resolve database path
        self.db_path = base_path / "cache" / "indexes" / "ast" / "ast_index.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lazy-load dependencies
        self._conn: Optional[sqlite3.Connection] = None
        self._parsers: Dict[str, Any] = {}  # Language -> tree-sitter Parser
        
        logger.info("ASTIndex initialized (lazy-load mode)")
    
    def _ensure_connection(self):
        """Ensure SQLite connection is established (lazy initialization)."""
        if self._conn is None:
            try:
                self._conn = sqlite3.connect(str(self.db_path))
                self._conn.row_factory = sqlite3.Row
                logger.info("Connected to SQLite at %s", self.db_path)
                
                # Initialize schema
                self._initialize_schema()
                
            except Exception as e:
                raise ActionableError(
                    what_failed="SQLite connection",
                    why_failed=str(e),
                    how_to_fix="Check that cache/indexes/ast/ directory is writable"
                ) from e
    
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        try:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS ast_nodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    language TEXT NOT NULL,
                    node_type TEXT NOT NULL,
                    symbol_name TEXT,
                    start_line INTEGER NOT NULL,
                    end_line INTEGER NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES ast_nodes(id)
                )
            """)
            
            # Create indexes for performance
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_file_path ON ast_nodes(file_path)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_node_type ON ast_nodes(node_type)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_language ON ast_nodes(language)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_symbol_name ON ast_nodes(symbol_name)
            """)
            
            self._conn.commit()
            logger.info("✅ SQLite schema initialized")
            
        except Exception as e:
            raise IndexError(
                what_failed="Initialize SQLite schema",
                why_failed=str(e),
                how_to_fix="Check server logs. Database may be corrupted."
            ) from e
    
    def _ensure_parser(self, language: str):
        """Ensure tree-sitter parser is loaded for a language.
        
        Args:
            language: Language name (e.g., "python", "typescript")
            
        Raises:
            ActionableError: If parser cannot be loaded
        """
        if language not in self._parsers:
            try:
                import tree_sitter_languages
                
                # Get parser for language
                parser = tree_sitter_languages.get_parser(language)
                self._parsers[language] = parser
                logger.info("✅ Loaded tree-sitter parser for %s", language)
                
            except ImportError as e:
                raise ActionableError(
                    what_failed=f"Load tree-sitter parser for {language}",
                    why_failed="tree-sitter-languages package not installed",
                    how_to_fix="Install via: pip install 'tree-sitter-languages>=1.10.0'"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed=f"Load tree-sitter parser for {language}",
                    why_failed=str(e),
                    how_to_fix=f"Ensure language '{language}' is supported by tree-sitter-languages"
                ) from e
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build AST index from source paths.
        
        This method:
        1. Parses source files using tree-sitter
        2. Extracts AST nodes (functions, classes, etc.)
        3. Stores metadata in SQLite
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building AST index from %d source paths", len(source_paths))
        
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        # Clear existing data if force rebuild
        if force:
            logger.info("Clearing existing AST data (force rebuild)")
            self._conn.execute("DELETE FROM ast_nodes")
            self._conn.commit()
        
        # Check if index already has data
        cursor = self._conn.execute("SELECT COUNT(*) FROM ast_nodes")
        node_count = cursor.fetchone()[0]
        if node_count > 0 and not force:
            logger.info("AST index already exists with %d nodes. Use force=True to rebuild.", node_count)
            return
        
        # Collect and parse source files
        ast_nodes = self._extract_ast_data(source_paths)
        
        if not ast_nodes:
            raise ActionableError(
                what_failed="Build AST index",
                why_failed="No AST nodes found in source paths",
                how_to_fix=f"Check that source paths contain code files for languages: {self.config.languages}"
            )
        
        # Insert AST nodes
        logger.info("Inserting %d AST nodes into SQLite...", len(ast_nodes))
        self._conn.executemany(
            "INSERT INTO ast_nodes (file_path, language, node_type, symbol_name, start_line, end_line, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ast_nodes
        )
        self._conn.commit()
        
        logger.info("✅ AST index built successfully")
    
    def _extract_ast_data(self, source_paths: List[Path]) -> List[Tuple]:
        """Extract AST nodes from source code.
        
        This is a placeholder implementation that returns empty results.
        A full implementation would:
        1. Parse files with tree-sitter
        2. Walk AST and extract nodes
        3. Filter by configured node types
        
        Args:
            source_paths: Paths to scan for code files
            
        Returns:
            List of (file_path, language, node_type, symbol_name, start_line, end_line, parent_id)
        """
        logger.warning("AST extraction is a placeholder. Tree-sitter integration requires more detailed implementation.")
        
        # TODO: Implement tree-sitter-based AST extraction
        # For now, return empty to satisfy the build flow
        ast_nodes: List[Tuple] = []
        
        # Placeholder logic (would actually parse with tree-sitter)
        file_extensions = self._get_file_extensions()
        
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            if resolved_path.is_file():
                if resolved_path.suffix in file_extensions:
                    # Would parse with tree-sitter here
                    pass
            else:
                for ext in file_extensions:
                    for code_file in resolved_path.rglob(f"*{ext}"):
                        if self._should_skip_path(code_file):
                            continue
                        # Would parse with tree-sitter here
                        pass
        
        return ast_nodes
    
    def _get_file_extensions(self) -> List[str]:
        """Get file extensions for configured languages."""
        extension_map = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".mjs", ".cjs"],
            "typescript": [".ts", ".tsx"],
            "go": [".go"],
            "rust": [".rs"],
        }
        
        extensions = []
        for lang in self.config.languages:
            lang_lower = lang.lower()
            if lang_lower in extension_map:
                extensions.extend(extension_map[lang_lower])
        
        return extensions
    
    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = [
            "node_modules",
            "__pycache__",
            ".venv",
            "venv",
            "dist",
            "build",
            ".git",
        ]
        
        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search AST index by node type or symbol name.
        
        This is a basic search that queries by node_type or symbol_name.
        More advanced structural queries would be implemented later.
        
        Args:
            query: Node type (e.g., "function_definition") or symbol name
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type)
            
        Returns:
            List of SearchResult objects
        """
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            # Build WHERE clause
            where_clauses = []
            params: List[Any] = []
            
            # Query can be node type or symbol name
            where_clauses.append("(node_type LIKE ? OR symbol_name LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
            
            # Apply filters
            if filters:
                if "language" in filters:
                    where_clauses.append("language = ?")
                    params.append(filters["language"])
                if "node_type" in filters:
                    where_clauses.append("node_type = ?")
                    params.append(filters["node_type"])
                if "file_path" in filters:
                    where_clauses.append("file_path LIKE ?")
                    params.append(f"%{filters['file_path']}%")
            
            where_clause = " AND ".join(where_clauses)
            
            sql_query = f"""
                SELECT file_path, language, node_type, symbol_name, start_line, end_line
                FROM ast_nodes
                WHERE {where_clause}
                LIMIT ?
            """
            params.append(n_results)
            
            cursor = self._conn.execute(sql_query, params)
            results = cursor.fetchall()
            
            search_results = []
            for row in results:
                search_results.append(SearchResult(
                    content=f"{row['node_type']} {row['symbol_name'] or ''} (lines {row['start_line']}-{row['end_line']})",
                    file_path=row["file_path"],
                    relevance_score=1.0,
                    content_type="code",
                    metadata={
                        "language": row["language"],
                        "node_type": row["node_type"],
                        "symbol_name": row["symbol_name"],
                    },
                    line_range=(row["start_line"], row["end_line"])
                ))
            
            logger.info("AST search returned %d results for query: %s", len(search_results), query)
            return search_results
            
        except Exception as e:
            logger.error("AST search failed: %s", e, exc_info=True)
            raise IndexError(
                what_failed="AST search",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure AST index is built."
            ) from e
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update AST index for changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails
        """
        logger.info("Updating AST index with %d changed files", len(changed_files))
        
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            for file_path in changed_files:
                relative_path = str(file_path.relative_to(self.base_path))
                
                # Delete existing nodes for this file
                self._conn.execute(
                    "DELETE FROM ast_nodes WHERE file_path = ?",
                    [relative_path]
                )
                
                # Re-extract and insert if file still exists
                if file_path.exists():
                    # TODO: Extract AST nodes for this file
                    logger.info("Would re-extract AST nodes from %s", file_path)
            
            self._conn.commit()
            logger.info("✅ AST index updated")
            
        except Exception as e:
            logger.error("Failed to update AST index: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Update AST index",
                why_failed=str(e),
                how_to_fix="Check server logs. May need to rebuild if corruption detected."
            ) from e
    
    def health_check(self) -> HealthStatus:
        """Check AST index health.
        
        Returns:
            HealthStatus with diagnostic info
        """
        try:
            self._ensure_connection()
            assert self._conn is not None  # Type guard: _ensure_connection() always sets this
            
            cursor = self._conn.execute("SELECT COUNT(*) FROM ast_nodes")
            node_count = cursor.fetchone()[0]
            
            if node_count == 0:
                return HealthStatus(
                    healthy=False,
                    message="AST index is empty (no nodes)",
                    details={"node_count": 0}
                )
            
            return HealthStatus(
                healthy=True,
                message=f"AST index operational ({node_count} nodes)",
                details={"node_count": node_count}
            )
            
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"AST index not healthy: {e}",
                details={"error": str(e)}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get AST index statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            self._ensure_connection()
            assert self._conn is not None  # Type guard: _ensure_connection() always sets this
            
            cursor = self._conn.execute("SELECT COUNT(*) FROM ast_nodes")
            node_count = cursor.fetchone()[0]
            
            return {
                "node_count": node_count,
                "db_path": str(self.db_path),
                "languages": self.config.languages,
            }
            
        except Exception as e:
            return {"error": str(e)}
