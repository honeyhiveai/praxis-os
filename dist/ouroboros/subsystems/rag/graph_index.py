"""Graph Index: Call graph traversal using DuckDB recursive CTEs.

This index provides call graph analysis (who calls what?) using DuckDB's
powerful recursive Common Table Expression (CTE) capabilities.

Unlike semantic code search (CodeIndex), graph traversal answers questions like:
- "Who calls this function?" (find_callers)
- "What does this function call?" (find_dependencies)
- "How does X reach Y?" (find_call_paths)

Architecture:
- DuckDB: Relational database optimized for analytical queries
- Two tables: symbols (nodes) and relationships (edges)
- Tree-sitter: AST parsing for symbol extraction
- Recursive CTEs: Efficient graph traversal with max_depth

Mission: Enable "trust but verify" - AI can trace function dependencies
to understand call flows and impact analysis.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ouroboros.config.schemas.indexes import GraphConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.utils.errors import ActionableError, IndexError

logger = logging.getLogger(__name__)


class GraphIndex(BaseIndex):
    """Call graph index using DuckDB for graph traversal.
    
    Provides graph traversal queries over code relationships:
    - find_callers: Reverse lookup (who calls this?)
    - find_dependencies: Forward lookup (what does this call?)
    - find_call_paths: Full path finding (how to reach X from Y?)
    
    Schema:
    - symbols: id, name, type, file_path, line_number
    - relationships: id, from_symbol_id, to_symbol_id, relationship_type
    
    Uses DuckDB's recursive CTEs for efficient graph traversal with cycle detection.
    """
    
    def __init__(self, config: GraphConfig, base_path: Path):
        """Initialize Graph Index.
        
        Args:
            config: GraphConfig from MCPConfig
            base_path: Base path for resolving relative paths
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Resolve database path
        self.db_path = base_path / "cache" / "indexes" / "graph" / "call_graph.duckdb"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Lazy-load dependencies
        self._conn: Optional[Any] = None
        
        logger.info("GraphIndex initialized (lazy-load mode)")
    
    def _ensure_connection(self):
        """Ensure DuckDB connection is established (lazy initialization)."""
        if self._conn is None:
            try:
                import duckdb
                
                # Connect to persistent DuckDB database
                self._conn = duckdb.connect(str(self.db_path))
                logger.info("Connected to DuckDB at %s", self.db_path)
                
                # Initialize schema if tables don't exist
                self._initialize_schema()
                
            except ImportError as e:
                raise ActionableError(
                    what_failed="DuckDB import",
                    why_failed="duckdb package not installed",
                    how_to_fix="Install via: pip install 'duckdb>=0.9.0'"
                ) from e
            except Exception as e:
                raise ActionableError(
                    what_failed="DuckDB connection",
                    why_failed=str(e),
                    how_to_fix="Check that cache/indexes/graph/ directory is writable"
                ) from e
    
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        try:
            # Create symbols table
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL
                )
            """)
            
            # Create relationships table
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY,
                    from_symbol_id INTEGER NOT NULL,
                    to_symbol_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    FOREIGN KEY (from_symbol_id) REFERENCES symbols(id),
                    FOREIGN KEY (to_symbol_id) REFERENCES symbols(id)
                )
            """)
            
            # Create indexes for performance
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_symbol_id)
            """)
            self._conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_symbol_id)
            """)
            
            logger.info("✅ DuckDB schema initialized")
            
        except Exception as e:
            raise IndexError(
                what_failed="Initialize DuckDB schema",
                why_failed=str(e),
                how_to_fix="Check server logs. Database may be corrupted."
            ) from e
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build call graph from source paths.
        
        This method:
        1. Parses source files using tree-sitter
        2. Extracts symbols (functions, classes, methods)
        3. Extracts call relationships
        4. Populates DuckDB tables
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if graph exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building call graph from %d source paths", len(source_paths))
        
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        # Clear existing data if force rebuild
        if force:
            logger.info("Clearing existing graph data (force rebuild)")
            self._conn.execute("DELETE FROM relationships")
            self._conn.execute("DELETE FROM symbols")
        
        # Check if graph already has data
        symbol_count = self._conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        if symbol_count > 0 and not force:
            logger.info("Call graph already exists with %d symbols. Use force=True to rebuild.", symbol_count)
            return
        
        # Collect and parse source files
        symbols, relationships = self._extract_graph_data(source_paths)
        
        if not symbols:
            raise ActionableError(
                what_failed="Build call graph",
                why_failed="No symbols found in source paths",
                how_to_fix="Check that source paths contain code files for supported languages"
            )
        
        # Insert symbols
        logger.info("Inserting %d symbols into DuckDB...", len(symbols))
        self._conn.executemany(
            "INSERT INTO symbols (id, name, type, file_path, line_number) VALUES (?, ?, ?, ?, ?)",
            symbols
        )
        
        # Insert relationships
        logger.info("Inserting %d relationships into DuckDB...", len(relationships))
        if relationships:
            self._conn.executemany(
                "INSERT INTO relationships (id, from_symbol_id, to_symbol_id, relationship_type) VALUES (?, ?, ?, ?)",
                relationships
            )
        
        logger.info("✅ Call graph built successfully")
    
    def _extract_graph_data(self, source_paths: List[Path]) -> Tuple[List[Tuple], List[Tuple]]:
        """Extract symbols and relationships from source code.
        
        This is a simplified placeholder. A full implementation would:
        1. Use tree-sitter to parse files
        2. Extract function/class definitions (symbols)
        3. Extract call expressions (relationships)
        4. Handle imports and inheritance
        
        For now, we'll return empty lists to satisfy the interface.
        Tree-sitter integration will be added in a follow-up task.
        
        Args:
            source_paths: Paths to scan for code files
            
        Returns:
            (symbols, relationships) tuple where:
            - symbols: List of (id, name, type, file_path, line_number)
            - relationships: List of (id, from_symbol_id, to_symbol_id, relationship_type)
        """
        logger.warning("Graph extraction is a placeholder. Tree-sitter integration pending.")
        
        # TODO: Implement tree-sitter-based extraction
        # For now, return empty to satisfy the build flow
        symbols: List[Tuple] = []
        relationships: List[Tuple] = []
        
        # Placeholder: Simulate extracting symbols from Python files
        # In reality, this would parse ASTs and extract actual symbols
        symbol_id = 0
        file_extensions = self._get_file_extensions()
        
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            if resolved_path.is_file():
                if resolved_path.suffix in file_extensions:
                    # Would extract symbols here
                    pass
            else:
                for ext in file_extensions:
                    for code_file in resolved_path.rglob(f"*{ext}"):
                        if self._should_skip_path(code_file):
                            continue
                        # Would extract symbols here
                        pass
        
        return symbols, relationships
    
    def _get_file_extensions(self) -> List[str]:
        """Get file extensions for configured languages."""
        extension_map = {
            "python": [".py"],
            "javascript": [".js", ".jsx", ".mjs", ".cjs"],
            "typescript": [".ts", ".tsx"],
            "go": [".go"],
            "rust": [".rs"],
        }
        
        # GraphConfig doesn't have languages - use default set
        default_languages = ["python", "javascript", "typescript", "go", "rust"]
        extensions = []
        for lang in default_languages:
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
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Uses recursive CTE to traverse the call graph upwards.
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth (default: 10)
            
        Returns:
            List of caller information with paths
            
        Raises:
            IndexError: If query fails
        """
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            # Recursive CTE to find all callers up to max_depth
            query = f"""
            WITH RECURSIVE callers AS (
                -- Base case: direct callers
                SELECT 
                    s1.id AS caller_id,
                    s1.name AS caller_name,
                    s1.type AS caller_type,
                    s1.file_path AS caller_file,
                    s1.line_number AS caller_line,
                    s2.id AS target_id,
                    s2.name AS target_name,
                    1 AS depth,
                    s1.name AS path
                FROM symbols s2
                JOIN relationships r ON s2.id = r.to_symbol_id
                JOIN symbols s1 ON r.from_symbol_id = s1.id
                WHERE s2.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: callers of callers
                SELECT 
                    s1.id,
                    s1.name,
                    s1.type,
                    s1.file_path,
                    s1.line_number,
                    c.target_id,
                    c.target_name,
                    c.depth + 1,
                    s1.name || ' -> ' || c.path
                FROM callers c
                JOIN relationships r ON c.caller_id = r.to_symbol_id
                JOIN symbols s1 ON r.from_symbol_id = s1.id
                WHERE c.depth < ? AND r.relationship_type = 'calls'
            )
            SELECT DISTINCT * FROM callers ORDER BY depth, caller_name
            """
            
            results = self._conn.execute(query, [symbol_name, max_depth]).fetchall()
            
            # Convert to dictionaries
            callers = []
            for row in results:
                callers.append({
                    "caller_id": row[0],
                    "caller_name": row[1],
                    "caller_type": row[2],
                    "caller_file": row[3],
                    "caller_line": row[4],
                    "target_id": row[5],
                    "target_name": row[6],
                    "depth": row[7],
                    "path": row[8],
                })
            
            logger.info("Found %d callers for '%s'", len(callers), symbol_name)
            return callers
            
        except Exception as e:
            logger.error("Failed to find callers: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_callers query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure call graph is built."
            ) from e
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Uses recursive CTE to traverse the call graph downwards.
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth (default: 10)
            
        Returns:
            List of dependency information with paths
            
        Raises:
            IndexError: If query fails
        """
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            # Recursive CTE to find all dependencies up to max_depth
            query = f"""
            WITH RECURSIVE dependencies AS (
                -- Base case: direct dependencies
                SELECT 
                    s2.id AS dep_id,
                    s2.name AS dep_name,
                    s2.type AS dep_type,
                    s2.file_path AS dep_file,
                    s2.line_number AS dep_line,
                    s1.id AS source_id,
                    s1.name AS source_name,
                    1 AS depth,
                    s2.name AS path
                FROM symbols s1
                JOIN relationships r ON s1.id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE s1.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: dependencies of dependencies
                SELECT 
                    s2.id,
                    s2.name,
                    s2.type,
                    s2.file_path,
                    s2.line_number,
                    d.source_id,
                    d.source_name,
                    d.depth + 1,
                    d.path || ' -> ' || s2.name
                FROM dependencies d
                JOIN relationships r ON d.dep_id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE d.depth < ? AND r.relationship_type = 'calls'
            )
            SELECT DISTINCT * FROM dependencies ORDER BY depth, dep_name
            """
            
            results = self._conn.execute(query, [symbol_name, max_depth]).fetchall()
            
            # Convert to dictionaries
            dependencies = []
            for row in results:
                dependencies.append({
                    "dep_id": row[0],
                    "dep_name": row[1],
                    "dep_type": row[2],
                    "dep_file": row[3],
                    "dep_line": row[4],
                    "source_id": row[5],
                    "source_name": row[6],
                    "depth": row[7],
                    "path": row[8],
                })
            
            logger.info("Found %d dependencies for '%s'", len(dependencies), symbol_name)
            return dependencies
            
        except Exception as e:
            logger.error("Failed to find dependencies: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_dependencies query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure call graph is built."
            ) from e
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Uses recursive CTE to find all paths connecting two symbols.
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length (default: 10)
            
        Returns:
            List of call paths (each path is a list of symbol names)
            
        Raises:
            IndexError: If query fails
        """
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            # Recursive CTE to find all paths from source to target
            query = f"""
            WITH RECURSIVE paths AS (
                -- Base case: start from source symbol
                SELECT 
                    s1.id AS current_id,
                    s1.name AS current_name,
                    s2.id AS next_id,
                    s2.name AS next_name,
                    1 AS depth,
                    s1.name || ' -> ' || s2.name AS path,
                    s1.name || ',' || s2.name AS visited_ids
                FROM symbols s1
                JOIN relationships r ON s1.id = r.from_symbol_id
                JOIN symbols s2 ON r.to_symbol_id = s2.id
                WHERE s1.name = ? AND r.relationship_type = 'calls'
                
                UNION ALL
                
                -- Recursive case: extend paths
                SELECT 
                    s2.id,
                    s2.name,
                    s3.id,
                    s3.name,
                    p.depth + 1,
                    p.path || ' -> ' || s3.name,
                    p.visited_ids || ',' || s3.name
                FROM paths p
                JOIN relationships r ON p.next_id = r.from_symbol_id
                JOIN symbols s2 ON p.next_id = s2.id
                JOIN symbols s3 ON r.to_symbol_id = s3.id
                WHERE 
                    p.depth < ? 
                    AND r.relationship_type = 'calls'
                    AND p.visited_ids NOT LIKE '%' || s3.name || '%'  -- Cycle detection
            )
            SELECT DISTINCT path FROM paths WHERE next_name = ?
            """
            
            results = self._conn.execute(query, [from_symbol, max_depth, to_symbol]).fetchall()
            
            # Convert paths to lists
            call_paths = []
            for row in results:
                path_str = row[0]
                path_list = path_str.split(" -> ")
                call_paths.append(path_list)
            
            logger.info("Found %d paths from '%s' to '%s'", len(call_paths), from_symbol, to_symbol)
            return call_paths
            
        except Exception as e:
            logger.error("Failed to find call paths: %s", e, exc_info=True)
            raise IndexError(
                what_failed="find_call_paths query",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure call graph is built."
            ) from e
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """Search symbols by name (for BaseIndex interface compatibility).
        
        This is a basic symbol search, not graph traversal.
        For graph queries, use find_callers/find_dependencies/find_call_paths.
        
        Args:
            query: Symbol name or pattern to search
            n_results: Max results to return
            filters: Optional filters (type, file_path)
            
        Returns:
            List of SearchResult objects
        """
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            # Simple symbol search
            sql_query = "SELECT name, type, file_path, line_number FROM symbols WHERE name LIKE ? LIMIT ?"
            results = self._conn.execute(sql_query, [f"%{query}%", n_results]).fetchall()
            
            search_results = []
            for row in results:
                search_results.append(SearchResult(
                    content=f"{row[1]} {row[0]} at line {row[3]}",
                    file_path=row[2],
                    relevance_score=1.0,
                    content_type="code",
                    metadata={"symbol_type": row[1], "symbol_name": row[0]},
                    line_range=(row[3], row[3])
                ))
            
            return search_results
            
        except Exception as e:
            logger.error("Symbol search failed: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Symbol search",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure call graph is built."
            ) from e
    
    def update(self, changed_files: List[Path]) -> None:
        """Incrementally update call graph for changed files.
        
        Args:
            changed_files: Files that have been added/modified/deleted
            
        Raises:
            ActionableError: If update fails
        """
        logger.info("Updating call graph with %d changed files", len(changed_files))
        
        self._ensure_connection()
        assert self._conn is not None  # Type guard: _ensure_connection() always sets this
        
        try:
            for file_path in changed_files:
                relative_path = str(file_path.relative_to(self.base_path))
                
                # Delete symbols and relationships for this file
                symbol_ids = self._conn.execute(
                    "SELECT id FROM symbols WHERE file_path = ?",
                    [relative_path]
                ).fetchall()
                
                if symbol_ids:
                    symbol_ids_list = [row[0] for row in symbol_ids]
                    placeholders = ",".join(["?" for _ in symbol_ids_list])
                    
                    # Delete relationships
                    self._conn.execute(
                        f"DELETE FROM relationships WHERE from_symbol_id IN ({placeholders}) OR to_symbol_id IN ({placeholders})",
                        symbol_ids_list + symbol_ids_list
                    )
                    
                    # Delete symbols
                    self._conn.execute(
                        f"DELETE FROM symbols WHERE id IN ({placeholders})",
                        symbol_ids_list
                    )
                
                # Re-extract and insert if file still exists
                if file_path.exists():
                    # TODO: Extract symbols and relationships for this file
                    # For now, just log
                    logger.info("Would re-extract symbols from %s", file_path)
            
            logger.info("✅ Call graph updated")
            
        except Exception as e:
            logger.error("Failed to update call graph: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Update call graph",
                why_failed=str(e),
                how_to_fix="Check server logs. May need to rebuild if corruption detected."
            ) from e
    
    def health_check(self) -> HealthStatus:
        """Check graph health.
        
        Returns:
            HealthStatus with diagnostic info
        """
        try:
            self._ensure_connection()
            assert self._conn is not None  # Type guard: _ensure_connection() always sets this
            
            symbol_count = self._conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            rel_count = self._conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            
            if symbol_count == 0:
                return HealthStatus(
                    healthy=False,
                    message="Call graph is empty (no symbols)",
                    details={"symbol_count": 0, "relationship_count": 0}
                )
            
            return HealthStatus(
                healthy=True,
                message=f"Call graph operational ({symbol_count} symbols, {rel_count} relationships)",
                details={"symbol_count": symbol_count, "relationship_count": rel_count}
            )
            
        except Exception as e:
            return HealthStatus(
                healthy=False,
                message=f"Call graph not healthy: {e}",
                details={"error": str(e)}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            self._ensure_connection()
            assert self._conn is not None  # Type guard: _ensure_connection() always sets this
            
            symbol_count = self._conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
            rel_count = self._conn.execute("SELECT COUNT(*) FROM relationships").fetchone()[0]
            
            return {
                "symbol_count": symbol_count,
                "relationship_count": rel_count,
                "db_path": str(self.db_path),
            }
            
        except Exception as e:
            return {"error": str(e)}

