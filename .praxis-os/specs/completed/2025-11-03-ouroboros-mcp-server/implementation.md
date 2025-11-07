# Implementation Approach

**Project:** Ouroboros MCP Server (Clean Architecture Rewrite)  
**Date:** 2025-11-04

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Behavioral Engineering First** - The mission is enabling praxis, not just building features
2. **Fail-Fast Validation** - Invalid state should crash immediately with actionable errors
3. **Config-Driven Extensibility** - Add languages/features via config, not code changes
4. **Test at All Layers** - Unit → Integration → Performance → Validation
5. **Incremental Delivery** - Each phase should be functional and testable
6. **Zero Cross-Talk** - Subsystems never call each other directly

---

## 2. Implementation Order

Follow the phases defined in `tasks.md`:

1. **Phase 1: Foundation** (Config + Utils) - 6-8 hours
2. **Phase 2: Core Infrastructure** (Registry + Middleware) - 8-10 hours
3. **Phase 3: RAG Subsystem** (Search + Indexes) - 16-20 hours
4. **Phase 4: Workflow Subsystem** - 8-10 hours
5. **Phase 5: Browser Subsystem** - 4-6 hours
6. **Phase 6: Tools Layer** - 6-8 hours
7. **Phase 7: Entry Points** - 4-6 hours
8. **Phase 8: Testing + Validation** - 12-16 hours

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 6 → Phase 7 → Phase 8

**Note:** Phases 4 and 5 can proceed in parallel with Phase 3 if multiple developers are available.

---

## 3. Code Patterns

### 3.1 Pydantic Configuration Pattern

**Purpose:** Type-safe, validated configuration with fail-fast errors

**Used in:** All components (Phase 1)

**Pattern:**
```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from pathlib import Path

class StandardsIndexConfig(BaseModel):
    """Configuration for standards index with hybrid search."""
    
    # Required fields with validation
    source_paths: list[Path] = Field(
        ...,  # Required
        description="Paths to index (relative to .praxis-os/)",
        min_length=1
    )
    
    # Fields with defaults and constraints
    chunk_size: int = Field(
        default=512,
        ge=100,  # >= 100
        le=2048,  # <= 2048
        description="Chunk size for text splitting"
    )
    
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        pattern=r"^[a-zA-Z0-9/_-]+$",
        description="Sentence-transformers model name"
    )
    
    # Nested config
    vector: VectorConfig
    fts: FTSConfig
    reranking: Optional[RerankingConfig] = None
    
    # Cross-field validation
    @field_validator("reranking")
    @classmethod
    def reranking_requires_vector(cls, v, values):
        if v is not None and not values.data.get("vector"):
            raise ValueError("Reranking requires vector search to be enabled")
        return v
    
    # Property for derived values
    @property
    def index_path(self) -> Path:
        return Path(".praxis-os/.cache/vector_index/standards")
```

**✅ Good:**
- Use `Field()` for all constraints and descriptions
- Use `@field_validator` for cross-field validation
- Use `Literal` for enum-like fields
- Provide sensible defaults
- Make errors actionable (`pattern` with regex)

**❌ Anti-Pattern:**
```python
# NO: No validation, stringly-typed
class Config:
    def __init__(self, chunk_size, model):
        self.chunk_size = chunk_size  # Could be negative!
        self.model = model  # Could be None!
```

---

### 3.2 FastMCP Tool Pattern (Domain Abstraction)

**Purpose:** Expose subsystems to AI agents with action-based interface

**Used in:** All tools (Phase 6)

**Pattern:**
```python
from fastmcp import FastMCP
from typing import Literal, Optional, Dict, Any

mcp = FastMCP("ouroboros")

@mcp.tool()
async def pos_search_project(
    action: Literal[
        "search_standards",  # Semantic search over standards
        "search_code",       # Semantic search over code
        "search_ast",        # Structural AST search
        "find_callers",      # Graph: who calls this?
        "find_dependencies", # Graph: what does this call?
        "find_paths"         # Graph: show call chain
    ],
    query: str,
    method: Literal["hybrid", "vector", "fts"] = "hybrid",
    max_results: int = 5,
    max_depth: int = 10,  # For graph actions
    to_symbol: Optional[str] = None,  # For find_paths
    **kwargs
) -> Dict[str, Any]:
    """
    Unified project search tool.
    
    Actions:
    - search_standards: Hybrid search (vector + FTS + rerank) over standards docs
    - search_code: Semantic search over code (LanceDB + CodeBERT)
    - search_ast: Structural search (Tree-sitter AST)
    - find_callers: Graph traversal (DuckDB recursive CTE) - who calls this?
    - find_dependencies: What does this symbol call?
    - find_paths: Show call chain from A to B
    
    Returns:
        Dict with keys: status, results, metadata, prepend
    """
    # Step 1: Query tracking (middleware)
    query_record = query_tracker.record(action=action, query=query)
    
    try:
        # Step 2: Route to correct index
        if action == "search_standards":
            results = await index_manager.get_index("standards").search(
                query, method=method, max_results=max_results
            )
        elif action == "search_code":
            results = await index_manager.get_index("code").search(
                query, method=method, max_results=max_results
            )
        elif action == "search_ast":
            results = await index_manager.get_index("ast").search(query, **kwargs)
        elif action == "find_callers":
            results = await index_manager.get_index("graph").find_callers(
                query, max_depth=max_depth
            )
        elif action == "find_dependencies":
            results = await index_manager.get_index("graph").find_dependencies(
                query, max_depth=max_depth
            )
        elif action == "find_paths":
            if not to_symbol:
                raise ValueError("find_paths requires 'to_symbol' parameter")
            results = await index_manager.get_index("graph").find_call_paths(
                query, to_symbol, max_depth=max_depth
            )
        
        # Step 3: Generate prepend (middleware)
        prepend = prepend_generator.generate(query_record)
        
        # Step 4: Return results with prepend
        return {
            "status": "success",
            "action": action,
            "query": query,
            "prepend": prepend,  # CRITICAL: Must be present
            "results": results,
            "metadata": {
                "result_count": len(results),
                "method": method,
                "latency_ms": query_record.latency_ms
            }
        }
    
    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        return {
            "status": "error",
            "action": action,
            "error": str(e),
            "remediation": _get_remediation(e)  # Actionable fix
        }
```

**✅ Good:**
- Use `Literal` for action enum (FastMCP converts to JSON Schema enum)
- Wrap with middleware (query tracking, prepend generation)
- Return prepend in 100% of results
- Fail-fast with actionable remediation
- Use async for I/O-bound operations

**❌ Anti-Pattern:**
```python
# NO: No Literal (action not discoverable), no prepend, silent failures
@mcp.tool()
def search(content_type: str, query: str):  # str not Literal!
    try:
        results = index.search(query)
        return results  # NO PREPEND!
    except:
        return []  # SILENT FAILURE!
```

---

### 3.3 Middleware Pattern (Behavioral Engineering)

**Purpose:** Wrap all tool calls to inject behavioral reinforcement

**Used in:** All tools (Phase 2)

**Pattern:**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class QueryRecord:
    timestamp: datetime
    session_id: str
    action: str
    query: str
    method: str
    result_count: int
    latency_ms: float
    angle_detected: str  # 📖 conceptual, 📍 location, 🔧 implementation, etc.

class PrependGenerator:
    """Generate query gamification prepends."""
    
    def __init__(self, query_tracker: QueryTracker):
        self.query_tracker = query_tracker
    
    def generate(self, query_record: QueryRecord) -> str:
        """
        Generate prepend for search result.
        
        Format:
            📊 Queries: 4/5 | Unique: 3 | Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜
            💡 Try: 'Where is X implemented?' (📍 location angle)
        """
        # Get session stats
        session_stats = self.query_tracker.get_session_stats(query_record.session_id)
        
        # Calculate diversity
        angles_used = len(session_stats.angles_used)
        diversity_pct = (angles_used / 5) * 100
        
        # Build progress bar
        query_count = session_stats.query_count
        unique_queries = session_stats.unique_queries
        
        # Build angle indicators
        angle_icons = {
            "conceptual": "📖",
            "location": "📍",
            "implementation": "🔧",
            "critical": "⭐",
            "troubleshooting": "⚠️"
        }
        
        angle_str = " ".join([
            f"{icon}{'✓' if angle in session_stats.angles_used else '⬜'}"
            for angle, icon in angle_icons.items()
        ])
        
        # Suggest next angle
        next_angle = self._suggest_next_angle(session_stats.angles_used)
        
        prepend = f"""📊 Queries: {query_count}/10 | Unique: {unique_queries} | Angles: {angle_str}
💡 Try: '{next_angle.suggestion}' ({next_angle.icon} {next_angle.name} angle)

---

"""
        
        return prepend
    
    def _suggest_next_angle(self, angles_used: set[str]) -> AngleSuggestion:
        """Suggest an unused angle to encourage diversity."""
        suggestions = {
            "conceptual": AngleSuggestion(
                "📖", "conceptual", "What is the conceptual foundation of X?"
            ),
            "location": AngleSuggestion(
                "📍", "location", "Where is X implemented?"
            ),
            # ... etc
        }
        
        for angle, suggestion in suggestions.items():
            if angle not in angles_used:
                return suggestion
        
        # All angles used - suggest conceptual again
        return suggestions["conceptual"]
```

**✅ Good:**
- Generate prepend for 100% of searches (no exceptions)
- Use session-level stats for diversity calculation
- Provide actionable suggestions
- **Fail the request if prepend generation fails** (no silent degradation)

**❌ Anti-Pattern:**
```python
# NO: Silent failure, no prepend
def generate_prepend(query):
    try:
        return f"Query: {query}"
    except:
        return ""  # SILENT DEGRADATION - violates behavioral mission!
```

---

### 3.4 LanceDB Hybrid Search Pattern

**Purpose:** Semantic + FTS + RRF fusion for high-quality search

**Used in:** StandardsIndex, CodeIndex (Phase 3)

**Pattern:**
```python
import lancedb
from sentence_transformers import SentenceTransformer

class StandardsIndex:
    """Hybrid search over standards content."""
    
    def __init__(self, config: StandardsIndexConfig):
        self.config = config
        self.db = lancedb.connect(config.index_path)
        self.model = SentenceTransformer(config.embedding_model)
        self.table = None
    
    def build(self, force_rebuild: bool = False):
        """Build or rebuild the index."""
        # Load documents
        docs = self._load_documents(self.config.source_paths)
        
        # Chunk documents
        chunks = self._chunk_documents(docs, self.config.chunk_size)
        
        # Generate embeddings
        embeddings = self.model.encode(
            [c.content for c in chunks],
            batch_size=32,
            show_progress_bar=True
        )
        
        # Create table
        data = [
            {
                "id": chunk.id,
                "content": chunk.content,
                "file_path": chunk.file_path,
                "framework_type": chunk.metadata.get("framework_type"),
                "phase": chunk.metadata.get("phase"),
                "is_critical": chunk.metadata.get("is_critical", False),
                "vector": embedding.tolist()
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]
        
        self.table = self.db.create_table(
            "standards",
            data=data,
            mode="overwrite" if force_rebuild else "create"
        )
        
        # Create FTS index
        self.table.create_fts_index("content", use_tantivy=False, replace=True)
        
        # Create scalar indexes for metadata filtering
        self.table.create_scalar_index("framework_type", index_type="BTREE", replace=True)
        self.table.create_scalar_index("phase", index_type="BITMAP", replace=True)
        self.table.create_scalar_index("is_critical", index_type="BITMAP", replace=True)
    
    async def search(
        self,
        query: str,
        method: Literal["hybrid", "vector", "fts"] = "hybrid",
        max_results: int = 5,
        filter: Optional[str] = None
    ) -> list[SearchResult]:
        """
        Search with hybrid (vector + FTS + RRF) method.
        
        Args:
            query: Search query
            method: Search method (hybrid, vector, fts)
            max_results: Number of results to return
            filter: Optional SQL filter (e.g., "phase = 3 AND is_critical = true")
        
        Returns:
            List of search results ranked by relevance
        """
        if method == "vector":
            return await self._vector_search(query, max_results, filter)
        elif method == "fts":
            return await self._fts_search(query, max_results, filter)
        elif method == "hybrid":
            return await self._hybrid_search(query, max_results, filter)
    
    async def _hybrid_search(
        self,
        query: str,
        max_results: int,
        filter: Optional[str]
    ) -> list[SearchResult]:
        """Hybrid search with RRF fusion."""
        # Get top-2k from each method
        vector_results = await self._vector_search(query, max_results=2000, filter=filter)
        fts_results = await self._fts_search(query, max_results=2000, filter=filter)
        
        # RRF fusion (Reciprocal Rank Fusion)
        fused = self._rrf_fusion(
            [vector_results, fts_results],
            k=60  # RRF constant
        )
        
        # Take top-k
        top_results = fused[:max_results]
        
        # Optional: Re-rank with cross-encoder
        if self.config.reranking and self.config.reranking.enabled:
            top_results = await self._rerank(query, top_results)
        
        return top_results
    
    def _rrf_fusion(self, result_lists: list[list[SearchResult]], k: int = 60) -> list[SearchResult]:
        """Reciprocal Rank Fusion."""
        scores = {}
        
        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                doc_id = result.id
                score = 1 / (k + rank)
                scores[doc_id] = scores.get(doc_id, 0) + score
        
        # Sort by fused score
        fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Map back to results
        id_to_result = {r.id: r for results in result_lists for r in results}
        return [id_to_result[doc_id] for doc_id, _ in fused if doc_id in id_to_result]
    
    def incremental_update(self, file_path: Path, event_type: Literal["create", "modify", "delete"]):
        """Handle incremental index updates from file watcher."""
        if event_type == "delete":
            self.table.delete(f"file_path = '{file_path}'")
        else:  # create or modify
            # Remove old version
            self.table.delete(f"file_path = '{file_path}'")
            
            # Add new version
            chunks = self._chunk_file(file_path)
            embeddings = self.model.encode([c.content for c in chunks])
            
            records = [
                {
                    "id": chunk.id,
                    "content": chunk.content,
                    "file_path": str(file_path),
                    "vector": embedding.tolist(),
                    # ... metadata
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]
            
            self.table.add(records)
            
            # CRITICAL: Rebuild FTS index to include new rows
            self.table.create_fts_index("content", use_tantivy=False, replace=True)
            
            # CRITICAL: Rebuild scalar indexes
            self._rebuild_scalar_indexes()
```

**✅ Good:**
- Use hybrid search (vector + FTS + RRF) for best results
- Rebuild FTS and scalar indexes after incremental updates
- Batch embeddings (batch_size=32)
- Use `replace=True` for index rebuilds

**❌ Anti-Pattern:**
```python
# NO: No FTS rebuild after incremental update = corruption
def incremental_update(self, file_path):
    self.table.add(new_records)
    # MISSING: self.table.create_fts_index(..., replace=True)
    # Result: FTS index is stale, panics on search!
```

---

### 3.5 DuckDB Graph Traversal Pattern

**Purpose:** Query call graphs with recursive CTEs

**Used in:** GraphIndex (Phase 3)

**Pattern:**
```python
import duckdb
from typing import Optional

class GraphIndex:
    """Call graph traversal using DuckDB."""
    
    def __init__(self, config: GraphConfig):
        self.config = config
        self.conn = duckdb.connect(config.db_path)
        self._create_schema()
    
    def _create_schema(self):
        """Create symbols and relationships tables."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,  -- function, class, method
                file_path TEXT NOT NULL,
                line_number INTEGER NOT NULL,
                UNIQUE(name, file_path, line_number)
            );
            
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY,
                from_symbol_id INTEGER NOT NULL,
                to_symbol_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,  -- calls, imports, inherits
                FOREIGN KEY (from_symbol_id) REFERENCES symbols(id),
                FOREIGN KEY (to_symbol_id) REFERENCES symbols(id),
                UNIQUE(from_symbol_id, to_symbol_id, relationship_type)
            );
            
            CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
            CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_symbol_id);
            CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_symbol_id);
        """)
    
    def find_callers(self, symbol_name: str, max_depth: int = 10) -> list[CallPath]:
        """Find all functions that call this symbol (recursive)."""
        query = """
        WITH RECURSIVE callers AS (
            -- Base case: find the target symbol
            SELECT 
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                0 AS depth,
                CAST(s.name AS VARCHAR) AS path
            FROM symbols s
            WHERE s.name = ?
            
            UNION ALL
            
            -- Recursive case: find who calls the current set
            SELECT
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                c.depth + 1 AS depth,
                s.name || ' → ' || c.path AS path
            FROM symbols s
            JOIN relationships r ON r.to_symbol_id = c.id
            JOIN callers c ON r.from_symbol_id = s.id
            WHERE c.depth < ? AND r.relationship_type = 'calls'
        )
        SELECT DISTINCT * FROM callers WHERE depth > 0 ORDER BY depth, name;
        """
        
        results = self.conn.execute(query, [symbol_name, max_depth]).fetchall()
        
        return [
            CallPath(
                symbol_name=row[1],
                file_path=row[2],
                line_number=row[3],
                depth=row[4],
                path=row[5]
            )
            for row in results
        ]
    
    def find_dependencies(self, symbol_name: str, max_depth: int = 10) -> list[CallPath]:
        """Find all functions this symbol calls (recursive)."""
        query = """
        WITH RECURSIVE dependencies AS (
            -- Base case
            SELECT 
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                0 AS depth,
                CAST(s.name AS VARCHAR) AS path
            FROM symbols s
            WHERE s.name = ?
            
            UNION ALL
            
            -- Recursive case: find what the current set calls
            SELECT
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                d.depth + 1 AS depth,
                d.path || ' → ' || s.name AS path
            FROM symbols s
            JOIN relationships r ON r.from_symbol_id = d.id
            JOIN dependencies d ON r.to_symbol_id = s.id
            WHERE d.depth < ? AND r.relationship_type = 'calls'
        )
        SELECT DISTINCT * FROM dependencies WHERE depth > 0 ORDER BY depth, name;
        """
        
        results = self.conn.execute(query, [symbol_name, max_depth]).fetchall()
        
        return [
            CallPath(
                symbol_name=row[1],
                file_path=row[2],
                line_number=row[3],
                depth=row[4],
                path=row[5]
            )
            for row in results
        ]
    
    def find_call_paths(
        self,
        from_symbol: str,
        to_symbol: str,
        max_depth: int = 10
    ) -> list[CallPath]:
        """Find all call paths from A to B."""
        query = """
        WITH RECURSIVE paths AS (
            -- Base case: start at 'from_symbol'
            SELECT 
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                0 AS depth,
                CAST(s.name AS VARCHAR) AS path,
                false AS reached_target
            FROM symbols s
            WHERE s.name = ?
            
            UNION ALL
            
            -- Recursive case: follow calls
            SELECT
                s.id,
                s.name,
                s.file_path,
                s.line_number,
                p.depth + 1 AS depth,
                p.path || ' → ' || s.name AS path,
                s.name = ? AS reached_target
            FROM symbols s
            JOIN relationships r ON r.from_symbol_id = p.id
            JOIN paths p ON r.to_symbol_id = s.id
            WHERE p.depth < ? 
              AND r.relationship_type = 'calls'
              AND NOT p.reached_target  -- Stop after reaching target
        )
        SELECT DISTINCT * FROM paths WHERE reached_target = true ORDER BY depth, path;
        """
        
        results = self.conn.execute(query, [from_symbol, to_symbol, max_depth]).fetchall()
        
        return [
            CallPath(
                symbol_name=row[1],
                file_path=row[2],
                line_number=row[3],
                depth=row[4],
                path=row[5]
            )
            for row in results
        ]
```

**✅ Good:**
- Use recursive CTEs for graph traversal
- Add `max_depth` limit to prevent infinite recursion
- Create indexes on foreign keys
- Return call paths with depth

**❌ Anti-Pattern:**
```python
# NO: No max_depth = infinite loop risk
def find_callers(self, symbol_name):
    query = """
    WITH RECURSIVE callers AS (
        ...
        WHERE c.depth < 999999  -- Basically unlimited!
    )
    """
```

---

### 3.6 Tree-sitter AST Pattern

**Purpose:** Parse code into ASTs for structural search

**Used in:** ASTIndex (Phase 3)

**Pattern:**
```python
import tree_sitter
from tree_sitter import Language, Parser
from pathlib import Path

class ASTIndex:
    """Tree-sitter-based structural code search."""
    
    def __init__(self, config: ASTIndexConfig):
        self.config = config
        self.parsers = {}
        self._init_parsers()
    
    def _init_parsers(self):
        """Initialize Tree-sitter parsers for each language."""
        for lang_config in self.config.languages:
            if not lang_config.enabled:
                continue
            
            # Check if parser installed
            parser_path = Path(f".praxis-os/tree-sitter-{lang_config.name}")
            
            if not parser_path.exists() and self.config.auto_install_parsers:
                self._install_parser(lang_config.name)
            
            # Load parser
            language = Language(parser_path / "parser.so", lang_config.name)
            parser = Parser()
            parser.set_language(language)
            
            self.parsers[lang_config.name] = parser
    
    def _install_parser(self, language: str):
        """Auto-install Tree-sitter parser in isolated venv."""
        import subprocess
        
        # Use .praxis-os/venv for isolation
        venv_python = Path(".praxis-os/venv/bin/python")
        
        # Install parser
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", f"tree-sitter-{language}"],
            check=True,
            capture_output=True
        )
    
    def parse_file(self, file_path: Path) -> list[ASTNode]:
        """Parse file into AST and extract symbols."""
        # Detect language from file extension
        ext = file_path.suffix
        language = self._detect_language(ext)
        
        if language not in self.parsers:
            return []
        
        # Read file
        content = file_path.read_bytes()
        
        # Parse
        tree = self.parsers[language].parse(content)
        
        # Extract symbols (functions, classes, methods)
        symbols = []
        
        def traverse(node):
            if node.type in ["function_definition", "class_definition", "method_definition"]:
                name_node = node.child_by_field_name("name")
                if name_node:
                    symbols.append(ASTNode(
                        name=name_node.text.decode("utf-8"),
                        type=node.type,
                        file_path=str(file_path),
                        line_number=node.start_point[0] + 1,
                        source=content[node.start_byte:node.end_byte].decode("utf-8")
                    ))
            
            for child in node.children:
                traverse(child)
        
        traverse(tree.root_node)
        
        return symbols
    
    def search(self, query: str, symbol_type: Optional[str] = None) -> list[ASTNode]:
        """Search AST nodes by name and type."""
        # Query the database (stored AST nodes)
        # This is simplified - real implementation would use database
        
        results = []
        for node in self.ast_nodes:
            if query.lower() in node.name.lower():
                if symbol_type is None or node.type == symbol_type:
                    results.append(node)
        
        return results
```

**✅ Good:**
- Auto-install parsers if `auto_install_parsers = true`
- Use isolated venv for parser installation
- Extract function/class/method definitions
- Store AST nodes for search

**❌ Anti-Pattern:**
```python
# NO: Installing parsers in system Python = dependency conflicts
def install_parser(self, language):
    subprocess.run(["pip", "install", f"tree-sitter-{language}"])
    # Installs in system Python, conflicts with user's project!
```

---

### 3.7 Error Handling with Remediation Pattern

**Purpose:** Fail-fast with actionable error messages

**Used in:** All components

**Pattern:**
```python
class ConfigValidationError(Exception):
    """Configuration validation failed."""
    
    def __init__(self, field: str, value: Any, constraint: str, remediation: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        self.remediation = remediation
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        return f"""
Configuration Validation Error

Field: {self.field}
Value: {self.value}
Constraint: {self.constraint}

How to fix:
{self.remediation}

Config file: .praxis-os/config/mcp.yaml
"""

# Usage
if config.chunk_size < 100:
    raise ConfigValidationError(
        field="indexes.standards.chunk_size",
        value=config.chunk_size,
        constraint="must be >= 100",
        remediation="""
Update .praxis-os/config/mcp.yaml:

indexes:
  standards:
    chunk_size: 512  # Recommended: 512 (was {actual_value})

Why: Chunks smaller than 100 tokens don't contain enough context for semantic search.
"""
    )
```

**✅ Good:**
- Include field path, value, and constraint
- Provide concrete remediation steps
- Show example config fix
- Explain *why* the constraint exists

**❌ Anti-Pattern:**
```python
# NO: Vague error, no remediation
if config.chunk_size < 100:
    raise ValueError("Invalid chunk size")
    # Where? What's invalid? How to fix?
```

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Coverage Target:** ≥90% for Config, Registry, Middleware

**Pattern:**
```python
import pytest
from ouroboros.config.schemas.indexes import StandardsIndexConfig
from pydantic import ValidationError

def test_standards_index_config_valid():
    """Valid config should pass validation."""
    config = StandardsIndexConfig(
        source_paths=["standards/"],
        chunk_size=512,
        embedding_model="all-MiniLM-L6-v2",
        vector=VectorConfig(enabled=True),
        fts=FTSConfig(enabled=True)
    )
    
    assert config.chunk_size == 512
    assert config.index_path == Path(".praxis-os/.cache/vector_index/standards")

def test_chunk_size_too_small():
    """Chunk size below minimum should fail."""
    with pytest.raises(ValidationError) as exc_info:
        StandardsIndexConfig(
            source_paths=["standards/"],
            chunk_size=50,  # Below minimum (100)
            vector=VectorConfig(enabled=True)
        )
    
    assert "chunk_size" in str(exc_info.value)
    assert "100" in str(exc_info.value)

def test_reranking_requires_vector():
    """Reranking without vector search should fail."""
    with pytest.raises(ValidationError) as exc_info:
        StandardsIndexConfig(
            source_paths=["standards/"],
            vector=VectorConfig(enabled=False),
            reranking=RerankingConfig(enabled=True)  # Requires vector!
        )
    
    assert "reranking requires vector" in str(exc_info.value).lower()
```

**Testing Middleware:**
```python
def test_prepend_in_all_results():
    """Prepends MUST appear in 100% of search results."""
    query_tracker = QueryTracker()
    prepend_gen = PrependGenerator(query_tracker)
    
    query_record = QueryRecord(
        timestamp=datetime.now(),
        session_id="test-session",
        action="search_standards",
        query="how to test",
        method="hybrid",
        result_count=5,
        latency_ms=120,
        angle_detected="implementation"
    )
    
    prepend = prepend_gen.generate(query_record)
    
    # CRITICAL: Prepend must be present
    assert prepend.startswith("📊 Queries:")
    assert "💡 Try:" in prepend
    assert len(prepend) > 0

def test_query_tracker_logs_all_searches():
    """Every search MUST be logged."""
    query_tracker = QueryTracker()
    
    query_tracker.record(
        action="search_standards",
        query="test query",
        method="hybrid"
    )
    
    logs = query_tracker.get_logs()
    assert len(logs) == 1
    assert logs[0]["query"] == "test query"
```

---

### 4.2 Integration Tests

**Purpose:** Test subsystem interactions

**Pattern:**
```python
import pytest
from ouroboros.config.loader import load_config
from ouroboros.subsystems.rag.index_manager import IndexManager

@pytest.mark.integration
async def test_search_flow_end_to_end():
    """Test full search flow: config → index → middleware → results."""
    # Load config from actual YAML
    config = load_config(Path(".praxis-os/config/mcp.yaml"))
    
    # Initialize IndexManager
    index_manager = IndexManager(config.indexes)
    await index_manager.initialize()
    
    # Initialize middleware
    query_tracker = QueryTracker()
    prepend_gen = PrependGenerator(query_tracker)
    
    # Perform search
    query = "how to implement X"
    results = await index_manager.get_index("standards").search(query)
    
    # Record query
    query_record = query_tracker.record(
        action="search_standards",
        query=query,
        method="hybrid"
    )
    
    # Generate prepend
    prepend = prepend_gen.generate(query_record)
    
    # Validate
    assert len(results) > 0
    assert prepend.startswith("📊 Queries:")
    assert query_record.angle_detected in ["conceptual", "implementation"]

@pytest.mark.integration
async def test_config_loading_from_yaml():
    """Test loading config from actual .praxis-os/config/*.yaml files."""
    config = load_config(Path(".praxis-os/config/mcp.yaml"))
    
    assert config.version is not None
    assert config.indexes.standards is not None
    assert config.indexes.code is not None
    assert config.workflow is not None
```

---

### 4.3 Performance Tests

**Targets:**
- Cold start: <30s
- Search latency: <200ms (p95)
- Incremental update: <5s
- Config load: <100ms (p95)

**Pattern:**
```python
import pytest
import time

@pytest.mark.performance
async def test_cold_start_time():
    """Server cold start should complete in <30s."""
    start = time.time()
    
    # Simulate cold start
    config = load_config(Path(".praxis-os/config/mcp.yaml"))
    index_manager = IndexManager(config.indexes)
    await index_manager.initialize()
    
    elapsed = time.time() - start
    
    assert elapsed < 30, f"Cold start took {elapsed:.2f}s (target: <30s)"

@pytest.mark.performance
async def test_search_latency():
    """Hybrid search should complete in <200ms (p95)."""
    index_manager = get_test_index_manager()
    
    latencies = []
    for _ in range(100):
        start = time.time()
        await index_manager.get_index("standards").search("test query")
        latencies.append((time.time() - start) * 1000)
    
    p95 = sorted(latencies)[95]
    
    assert p95 < 200, f"Search p95 latency: {p95:.2f}ms (target: <200ms)"
```

---

### 4.4 Validation Tests (Behavioral Engineering)

**Purpose:** Ensure behavioral mission is functional

**Pattern:**
```python
@pytest.mark.validation
async def test_prepends_in_100_percent_of_searches():
    """Prepends must appear in 100% of search results (no exceptions)."""
    for _ in range(100):
        result = await pos_search_project(
            action="search_standards",
            query=f"test query {_}"
        )
        
        assert "prepend" in result
        assert result["prepend"].startswith("📊 Queries:")
        assert "💡 Try:" in result["prepend"]

@pytest.mark.validation
async def test_query_diversity_tracked():
    """Query diversity metrics must be accurate."""
    session_id = "test-session"
    
    # Query from 3 angles
    await pos_search_project(action="search_standards", query="what is X")  # conceptual
    await pos_search_project(action="search_standards", query="how to implement X")  # implementation
    await pos_search_project(action="search_standards", query="where is X")  # location
    
    metrics = query_tracker.get_session_stats(session_id)
    
    assert metrics.angles_used == {"conceptual", "implementation", "location"}
    assert metrics.diversity_score == 0.60  # 3/5 angles

@pytest.mark.validation
async def test_middleware_failure_fails_request():
    """If prepend generation fails, request must fail (no silent degradation)."""
    # Simulate prepend generator failure
    with pytest.raises(Exception) as exc_info:
        result = await pos_search_project_with_broken_middleware(
            action="search_standards",
            query="test"
        )
    
    assert "prepend generation failed" in str(exc_info.value).lower()
    # Request should NOT return results without prepend
```

---

## 5. Deployment Guidance

### 5.1 Initial Deployment

**Prerequisites:**
- Python 3.10+
- Existing `.praxis-os/` directory
- Valid `.praxis-os/config/mcp.yaml`

**Steps:**
```bash
# 1. Create ouroboros directory
mkdir -p .praxis-os/ouroboros

# 2. Copy source files (from implementation)
cp -r ouroboros/* .praxis-os/ouroboros/

# 3. Install dependencies in isolated venv
cd .praxis-os
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Validate config
python -m ouroboros.config.loader --validate

# 5. Test server startup
python -m ouroboros --log-level debug

# 6. Verify tools registered
python -m ouroboros --list-tools

# 7. Run validation tests
pytest tests/ouroboros/validation/ -v
```

---

### 5.2 Switching from mcp_server to ouroboros

**Transition Plan:**
1. Deploy ouroboros in parallel (`.praxis-os/ouroboros/`)
2. Run validation tests (feature parity)
3. Update `.mcp_server_state.json` to point to ouroboros
4. Restart Cursor (reload MCP server)
5. Monitor for issues (check `.praxis-os/logs/`)
6. Archive `mcp_server/` (do NOT delete until validated)

**Rollback Plan:**
```bash
# If issues found, rollback to mcp_server
cp .mcp_server_state.json.backup .mcp_server_state.json
# Restart Cursor
```

---

## 6. Troubleshooting

### 6.1 Config Validation Errors

**Symptom:** Server fails to start with `ValidationError`

**Solution:**
1. Check `.praxis-os/config/mcp.yaml` for syntax errors
2. Validate field constraints (chunk_size >= 100, etc.)
3. Check cross-field validation (reranking requires vector)
4. Run: `python -m ouroboros.config.loader --validate --verbose`

---

### 6.2 Index Not Building

**Symptom:** StandardsIndex or CodeIndex fails to build

**Solution:**
1. Check source paths exist: `ls .praxis-os/standards/`
2. Check embedding model installed: `pip list | grep sentence-transformers`
3. Check disk space: `df -h .praxis-os/.cache/`
4. Check logs: `tail -f .praxis-os/logs/ouroboros.log`

---

### 6.3 FTS Panics (LanceDB)

**Symptom:** Search fails with "called `Option::unwrap()` on a `None` value"

**Root Cause:** FTS index not rebuilt after incremental update

**Solution:**
- Implemented in `StandardsIndex.incremental_update()` (line 353-362)
- Always call `table.create_fts_index(..., replace=True)` after adding rows
- If corruption occurs: Rebuild index with `force_rebuild=True`

---

### 6.4 Prepends Not Appearing

**Symptom:** Search results missing prepends

**Root Cause:** Middleware not wrapping tool calls

**Solution:**
1. Check middleware initialization in server.py
2. Ensure PrependGenerator is called in tool implementation
3. Check for try/except swallowing errors (remove silent catches)
4. Run validation test: `pytest tests/ouroboros/validation/test_prepends.py`

---

### 6.5 Tree-sitter Parser Missing

**Symptom:** `ASTIndex` fails with "parser not found"

**Root Cause:** Parser not installed, or `auto_install_parsers = false`

**Solution:**
1. Enable auto-install: Set `auto_install_parsers: true` in config
2. Manual install: `pip install tree-sitter-{language}` in `.praxis-os/venv`
3. Check parser path: `ls .praxis-os/tree-sitter-{language}/`

---

## 7. Code Review Checklist

Before merging:
- [ ] All unit tests pass (≥90% coverage for core)
- [ ] All integration tests pass
- [ ] Performance targets met (cold start <30s, search <200ms)
- [ ] Validation tests pass (prepends in 100% of results)
- [ ] Pydantic configs have Field() constraints
- [ ] FastMCP tools use Literal for action enums
- [ ] Middleware wraps all tool calls
- [ ] Error messages include remediation
- [ ] No silent exceptions (no empty except blocks)
- [ ] Incremental updates rebuild FTS and scalar indexes
- [ ] Documentation updated

---

## 8. Related Documents

- **Design Doc:** `.praxis-os/workspace/design/2025-11-04-ouroboros-clean-architecture.md`
- **SRD:** `.praxis-os/specs/review/2025-11-03-ouroboros-mcp-server/srd.md`
- **Specs:** `.praxis-os/specs/review/2025-11-03-ouroboros-mcp-server/specs.md`
- **Tasks:** `.praxis-os/specs/review/2025-11-03-ouroboros-mcp-server/tasks.md`

---

**Implementation Ready:** ✅  
**Estimated Total Time:** 64-84 hours (8-10.5 days)  
**Critical Path:** 52-68 hours (6.5-8.5 days)

