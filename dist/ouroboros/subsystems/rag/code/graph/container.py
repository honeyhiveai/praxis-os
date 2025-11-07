"""GraphIndex container: Orchestrates AST extraction and graph traversal.

This module provides the main GraphIndex class that implements the BaseIndex
interface and coordinates:
1. AST extraction (parsing with tree-sitter)
2. Graph traversal (recursive CTEs in DuckDB)
3. DuckDB schema management
4. Index building and updates

Architecture:
- ASTExtractor: Handles tree-sitter parsing and data extraction
- GraphTraversal: Handles DuckDB queries (find_callers, search_ast, etc.)
- DuckDBConnection: Thread-safe database connection management

This is the internal implementation for CodeIndex graph operations.
Use CodeIndex (parent container) as the public interface.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ouroboros.config.schemas.indexes import GraphConfig
from ouroboros.subsystems.rag.base import BaseIndex, HealthStatus, SearchResult
from ouroboros.subsystems.rag.utils.duckdb_helpers import DuckDBConnection
from ouroboros.utils.errors import ActionableError, IndexError

from .ast import ASTExtractor
from .traversal import GraphTraversal

logger = logging.getLogger(__name__)


class GraphIndex(BaseIndex):
    """Unified AST + Call graph index using DuckDB.
    
    Combines structural code search (AST) with call graph traversal in a single
    DuckDB database. Orchestrates AST extraction and graph queries.
    
    Schema (DuckDB):
    1. ast_nodes: Structural code elements (functions, classes, methods)
    2. symbols: Callable symbols for graph analysis
    3. relationships: Call relationships between symbols
    
    Components:
    - ASTExtractor: Parse code and extract AST/symbols/relationships
    - GraphTraversal: Query graph using recursive CTEs
    
    Methods:
    - build(): Extract AST and build graph from source code
    - search(): Search symbols by name (BaseIndex interface)
    - search_ast(): Structural code search by pattern
    - find_callers(): Who calls this symbol? (reverse lookup)
    - find_dependencies(): What does this symbol call? (forward lookup)
    - find_call_paths(): How does X reach Y? (path finding)
    """
    
    def __init__(self, config: GraphConfig, base_path: Path, languages: Optional[List[str]] = None):
        """Initialize Graph Index.
        
        Args:
            config: GraphConfig from MCPConfig
            base_path: Base path for resolving relative paths
            languages: List of programming languages to support (e.g., ["python", "typescript"])
            
        Raises:
            ActionableError: If initialization fails
        """
        self.config = config
        self.base_path = base_path
        
        # Use provided languages or default to Python
        if languages is None:
            languages = ["python"]
            logger.warning("No languages specified for GraphIndex, defaulting to ['python']")
        
        self.languages = languages
        
        # Resolve database path
        self.db_path = base_path / ".cache" / "indexes" / "code" / "graph.duckdb"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection and components
        self.db_connection = DuckDBConnection(self.db_path)
        self.ast_extractor = ASTExtractor(
            languages=languages,
            base_path=base_path
        )
        self.traversal = GraphTraversal(self.db_connection)
        
        # Initialize schema
        self._initialize_schema()
        
        logger.info("GraphIndex initialized")
    
    def _initialize_schema(self):
        """Create DuckDB tables and indexes if they don't exist.
        
        Creates three tables:
        1. ast_nodes: Structural code elements
        2. symbols: Callable code symbols (graph nodes)
        3. relationships: Call relationships (graph edges)
        
        Raises:
            IndexError: If schema creation fails
        """
        try:
            conn = self.db_connection.get_connection()
            
            # Table 1: AST nodes (structural search)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ast_nodes (
                    id INTEGER PRIMARY KEY,
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
            
            # Indexes for AST queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_file_path ON ast_nodes(file_path)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_node_type ON ast_nodes(node_type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_language ON ast_nodes(language)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ast_symbol_name ON ast_nodes(symbol_name)
            """)
            
            # Table 2: Symbols (call graph nodes)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER NOT NULL,
                    language TEXT NOT NULL
                )
            """)
            
            # Indexes for symbol queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_type ON symbols(type)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbols_file_path ON symbols(file_path)
            """)
            
            # Table 3: Relationships (call graph edges)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY,
                    from_symbol_id INTEGER NOT NULL,
                    to_symbol_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    FOREIGN KEY (from_symbol_id) REFERENCES symbols(id),
                    FOREIGN KEY (to_symbol_id) REFERENCES symbols(id)
                )
            """)
            
            # Indexes for graph traversal
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_symbol_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_symbol_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type)
            """)
            
            logger.info("✅ DuckDB schema initialized (ast_nodes, symbols, relationships)")
            
        except Exception as e:
            raise IndexError(
                what_failed="Initialize DuckDB schema",
                why_failed=str(e),
                how_to_fix="Check server logs. Database may be corrupted or locked."
            ) from e
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build graph index from source paths.
        
        Implementation:
        1. Parse files with tree-sitter (via ASTExtractor)
        2. Extract AST nodes, symbols, and relationships
        3. Insert into DuckDB tables
        
        Args:
            source_paths: Paths to source directories
            force: If True, rebuild even if index exists
            
        Raises:
            ActionableError: If build fails
        """
        logger.info("Building graph index from %d source paths", len(source_paths))
        
        conn = self.db_connection.get_connection()
        
        # Clear existing data if force rebuild
        if force:
            logger.info("Clearing existing graph data (force rebuild)")
            conn.execute("DELETE FROM relationships")
            conn.execute("DELETE FROM symbols")
            conn.execute("DELETE FROM ast_nodes")
        
        # Check if index already has data
        ast_count = conn.execute("SELECT COUNT(*) FROM ast_nodes").fetchone()[0]
        symbol_count = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
        
        if ast_count > 0 and symbol_count > 0 and not force:
            logger.info("Graph index already exists with %d AST nodes and %d symbols. Use force=True to rebuild.",
                       ast_count, symbol_count)
            return
        
        # Extract data from source files
        ast_nodes, symbols, relationships = self._extract_all_data(source_paths)
        
        if not ast_nodes and not symbols:
            raise ActionableError(
                what_failed="Build graph index",
                why_failed="No AST nodes or symbols found in source paths",
                how_to_fix=f"Check that source paths contain code files for languages: {self.languages}. Ensure tree-sitter-languages is installed."
            )
        
        # Insert AST nodes
        if ast_nodes:
            logger.info("Inserting %d AST nodes into DuckDB...", len(ast_nodes))
            # DuckDB executemany for bulk insert
            conn.executemany(
                "INSERT INTO ast_nodes (id, file_path, language, node_type, symbol_name, start_line, end_line, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ast_nodes
            )
        
        # Insert symbols
        if symbols:
            logger.info("Inserting %d symbols into DuckDB...", len(symbols))
            conn.executemany(
                "INSERT INTO symbols (id, name, type, file_path, line_number, language) VALUES (?, ?, ?, ?, ?, ?)",
                symbols
            )
        
        # Insert relationships
        if relationships:
            logger.info("Inserting %d relationships into DuckDB...", len(relationships))
            conn.executemany(
                "INSERT INTO relationships (id, from_symbol_id, to_symbol_id, relationship_type) VALUES (?, ?, ?, ?)",
                relationships
            )
        
        logger.info("✅ Graph index built: %d AST nodes, %d symbols, %d relationships",
                   len(ast_nodes), len(symbols), len(relationships))
    
    def _extract_all_data(self, source_paths: List[Path]) -> tuple:
        """Extract AST nodes, symbols, and relationships from source code.
        
        Uses two-pass extraction to ensure cross-file relationships work correctly:
        1. Pass 1: Extract all symbols from all files (build complete symbol_map)
        2. Pass 2: Extract relationships using complete symbol_map
        
        Args:
            source_paths: Paths to scan for code files
            
        Returns:
            Tuple of (ast_nodes, symbols, relationships)
        """
        all_ast_nodes = []
        all_symbols = []
        all_relationships = []
        
        file_extensions = self.ast_extractor.get_file_extensions()
        
        ast_node_id = 0
        symbol_id = 0
        rel_id = 0
        
        # Collect all files to process
        files_to_process = []
        for source_path in source_paths:
            resolved_path = self.base_path / source_path
            
            if not resolved_path.exists():
                logger.warning("Source path does not exist: %s", resolved_path)
                continue
            
            if resolved_path.is_file():
                if resolved_path.suffix in file_extensions:
                    files_to_process.append(resolved_path)
            else:
                for ext in file_extensions:
                    for code_file in resolved_path.rglob(f"*{ext}"):
                        if self.ast_extractor.should_skip_path(code_file):
                            continue
                        files_to_process.append(code_file)
        
        # PASS 1: Extract AST nodes and symbols from ALL files
        # This builds a complete symbol_map before relationship extraction
        symbol_map = {}
        parsed_trees = []  # Cache parsed trees for pass 2
        
        logger.info("Pass 1: Extracting symbols from %d files...", len(files_to_process))
        
        for file_path in files_to_process:
            language = self.ast_extractor.detect_language(file_path)
            if not language:
                continue
            
            try:
                self.ast_extractor.ensure_parser(language)
                
                # Read and parse file
                with open(file_path, 'r', encoding='utf-8') as f:
                    code_bytes = f.read().encode('utf-8')
                
                parser = self.ast_extractor._parsers[language]
                tree = parser.parse(code_bytes)
                root_node = tree.root_node
                
                # Extract AST nodes
                ast_nodes = self.ast_extractor._extract_ast_nodes(
                    root_node, str(file_path), language, ast_node_id
                )
                
                # Extract symbols
                symbols = self.ast_extractor._extract_symbols(
                    root_node, str(file_path), language, symbol_id, code_bytes
                )
                
                # Update symbol_map
                for symbol in symbols:
                    sym_id, name, _, sym_file, _, _ = symbol
                    symbol_map[(sym_file, name)] = sym_id
                
                # Store for pass 2
                all_ast_nodes.extend(ast_nodes)
                all_symbols.extend(symbols)
                parsed_trees.append((file_path, root_node, language, code_bytes))
                
                # Update IDs
                if ast_nodes:
                    ast_node_id = max(node[0] for node in ast_nodes) + 1
                if symbols:
                    symbol_id = max(sym[0] for sym in symbols) + 1
                
                logger.debug("Pass 1: %s - %d AST nodes, %d symbols",
                            file_path.name, len(ast_nodes), len(symbols))
                
            except Exception as e:
                logger.warning("Failed to parse %s: %s", file_path, e)
                continue
        
        logger.info("Pass 1 complete: %d symbols extracted", len(all_symbols))
        
        # PASS 2: Extract relationships using complete symbol_map
        logger.info("Pass 2: Extracting relationships...")
        
        for file_path, root_node, language, code_bytes in parsed_trees:
            try:
                relationships = self.ast_extractor._extract_relationships(
                    root_node, str(file_path), language, rel_id, symbol_map, code_bytes
                )
                
                all_relationships.extend(relationships)
                
                # Update IDs
                if relationships:
                    rel_id = max(rel[0] for rel in relationships) + 1
                
                logger.debug("Pass 2: %s - %d relationships",
                            file_path.name, len(relationships))
                
            except Exception as e:
                logger.warning("Failed to extract relationships from %s: %s", file_path, e)
                continue
        
        logger.info("✅ Extracted: %d AST nodes, %d symbols, %d relationships",
                   len(all_ast_nodes), len(all_symbols), len(all_relationships))
        
        return all_ast_nodes, all_symbols, all_relationships
    
    # ========================================================================
    # BaseIndex Interface Methods
    # ========================================================================
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search symbols by name (BaseIndex interface).
        
        This is a basic symbol search for BaseIndex compatibility.
        For graph queries, use find_callers/find_dependencies/find_call_paths.
        For structural queries, use search_ast.
        
        Args:
            query: Symbol name or pattern to search
            n_results: Max results to return
            filters: Optional filters (type, file_path, language)
            
        Returns:
            List of SearchResult objects
            
        Raises:
            IndexError: If search fails
        """
        try:
            # Delegate to traversal's symbol search
            results = self.traversal.search_symbols(query, n_results, filters)
            
            # Convert to SearchResult objects
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    content=result["content"],
                    file_path=result["file_path"],
                    relevance_score=1.0,
                    content_type="code",
                    metadata={
                        "language": result["language"],
                        "symbol_type": result["type"],
                        "line_number": result["line_number"],
                    },
                    chunk_id=str(result["id"]),
                    line_range=(result["line_number"], result["line_number"])
                ))
            
            return search_results
            
        except Exception as e:
            logger.error("Failed to search: %s", e, exc_info=True)
            raise IndexError(
                what_failed="Search symbols",
                why_failed=str(e),
                how_to_fix="Check server logs. Ensure graph index is built."
            ) from e
    
    def update(self, file_paths: List[Path]) -> None:
        """Update index for changed files.
        
        For graph index, incremental updates are complex due to relationships.
        Recommend full rebuild for now.
        
        Args:
            file_paths: Paths to files that changed
        """
        logger.warning("GraphIndex.update() not yet implemented. Use build(force=True) for full rebuild.")
    
    def health_check(self) -> HealthStatus:
        """Check health of graph index.
        
        Returns:
            HealthStatus object
        """
        try:
            stats = self.traversal.get_stats()
            
            is_healthy = (
                stats["ast_node_count"] > 0 and
                stats["symbol_count"] > 0
            )
            
            return HealthStatus(
                healthy=is_healthy,
                message="Graph index healthy" if is_healthy else "Graph index empty or unhealthy",
                details={
                    "ast_node_count": stats["ast_node_count"],
                    "symbol_count": stats["symbol_count"],
                    "relationship_count": stats["relationship_count"],
                    "database_path": str(self.db_path),
                }
            )
            
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return HealthStatus(
                healthy=False,
                message=f"Health check failed: {e}",
                details={"error": str(e)}
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about graph index.
        
        Returns:
            Dict with ast_node_count, symbol_count, relationship_count
        """
        return self.traversal.get_stats()
    
    # ========================================================================
    # Extended Methods (Graph Operations)
    # ========================================================================
    
    def search_ast(
        self,
        pattern: str,
        n_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search AST nodes by pattern (structural search).
        
        Args:
            pattern: Node type or symbol name pattern
            n_results: Max results to return
            filters: Optional filters (language, file_path, node_type)
            
        Returns:
            List of AST node dicts
        """
        return self.traversal.search_ast(pattern, n_results, filters)
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find who calls the given symbol (reverse lookup).
        
        Args:
            symbol_name: Name of the symbol to find callers for
            max_depth: Maximum traversal depth
            
        Returns:
            List of caller information with paths
        """
        return self.traversal.find_callers(symbol_name, max_depth)
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """Find what the given symbol calls (forward lookup).
        
        Args:
            symbol_name: Name of the symbol to find dependencies for
            max_depth: Maximum traversal depth
            
        Returns:
            List of dependency information with paths
        """
        return self.traversal.find_dependencies(symbol_name, max_depth)
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> List[List[str]]:
        """Find call paths from one symbol to another.
        
        Args:
            from_symbol: Starting symbol name
            to_symbol: Target symbol name
            max_depth: Maximum path length
            
        Returns:
            List of call paths (each path is a list of symbol names)
        """
        return self.traversal.find_call_paths(from_symbol, to_symbol, max_depth)

