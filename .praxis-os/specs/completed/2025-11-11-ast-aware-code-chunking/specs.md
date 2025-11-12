# Technical Specifications

**Project:** AST-Aware Code Chunking with Import Penalty  
**Date:** 2025-11-11  
**Based on:** srd.md (Software Requirements Document)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Configuration-Driven Modular Architecture

The AST-Aware Code Chunking feature extends prAxIs OS's existing RAG (Retrieval-Augmented Generation) subsystem with a new modular component for Tree-sitter-based AST parsing and chunking. The design follows a configuration-driven approach where language-specific behavior is declaratively defined in `mcp.yaml` rather than hardcoded in Python, enabling scalability to 20+ languages without code changes.

**Pattern Characteristics:**
- **Modularity**: New AST chunking module integrates with existing SemanticIndex without breaking existing functionality
- **Configuration-Driven**: Language support added via `mcp.yaml` config (no code changes per language)
- **Layered Integration**: AST chunking operates at the index-building layer, transparent to search query layer
- **Graceful Degradation**: Fallback to line-based chunking ensures operational continuity

**Rationale:**
- **Addresses FR-004**: Configuration-driven language support
- **Addresses NFR-M1**: Maintainability through config-only language additions
- **Addresses NFR-R1**: Graceful degradation via fallback to line-based chunking
- **Benefits**:
  - Easy to extend (add languages via config)
  - Testable (mock configs for unit tests)
  - User-customizable (override penalties, node types)
  - Minimal disruption to existing code

---

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              mcp.yaml (Config)                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ indexes.code.language_configs:                                     │  │
│  │   python:   {chunking: {import_nodes, definition_nodes, ...}}     │  │
│  │   typescript: {chunking: {...}}                                    │  │
│  │   go:       {chunking: {...}}                                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ▲
                                    │ Config Read
         ┌──────────────────────────┴──────────────────────────┐
         │                                                       │
┌────────┴─────────────────────┐        ┌──────────────────────┴──────────┐
│    ASTExtractor              │        │  UniversalASTChunker (NEW)       │
│  (Refactored - ouroboros/    │        │  (New Module - ouroboros/        │
│   subsystems/rag/code/graph/ │        │   subsystems/rag/code/semantic/) │
│   ast.py)                    │        │                                  │
│                              │        │                                  │
│  - Reads node types from     │        │  - Reads chunking config         │
│    config                    │        │  - Chunks at AST boundaries      │
│  - Extracts AST nodes,       │        │  - Calculates import_ratio       │
│    symbols, relationships    │        │  - Applies import_penalty        │
│  - Shared Tree-sitter parser │◄───────┤  - Reuses ASTExtractor parser   │
└──────────────────────────────┘        └─────────┬────────────────────────┘
                                                  │ chunk_file()
                                                  │
                                        ┌─────────▼────────────────────────┐
                                        │  SemanticIndex (Modified)         │
                                        │  (ouroboros/subsystems/rag/code/  │
                                        │   semantic.py)                    │
                                        │                                   │
                                        │  - _chunk_file() → AST chunker    │
                                        │  - Falls back to line-based       │
                                        │  - Applies import penalty in RRF  │
                                        └───────────────────────────────────┘
                                                  │
                              ┌───────────────────┼───────────────────┐
                              │                   │                   │
                   ┌──────────▼──────────┐ ┌─────▼──────┐ ┌─────────▼────────┐
                   │  LanceDB Vector     │ │  LanceDB   │ │  RRF Ranking     │
                   │  Index (Embeddings) │ │  FTS Index │ │  (w/ Penalties)  │
                   └─────────────────────┘ └────────────┘ └──────────────────┘
```

**Data Flow:**
1. **Index Build Time**:
   - SemanticIndex calls UniversalASTChunker.chunk_file() for each source file
   - AST chunker reads language config from mcp.yaml
   - Tree-sitter parses file into AST
   - Chunks created at function/class boundaries
   - Import ratio calculated, penalty applied
   - Chunks stored in LanceDB with metadata (chunk_type, import_penalty, symbols)

2. **Query Time**:
   - User searches via `pos_search_project(action="search_code", query="...")`
   - Vector search (CodeBERT embeddings) + FTS search run in parallel
   - RRF fusion combines results
   - Import penalty applied to final ranking: `final_score = base_score * import_penalty`
   - Results returned ranked (implementations #1-2, imports #5+)

---

### 1.3 Architectural Decisions

#### Decision 1: Configuration-Driven Language Support

**Decision:** Define language-specific AST node types in `mcp.yaml` config instead of hardcoding in Python if/elif chains.

**Rationale:**
- **Addresses FR-004**: Configuration-driven language support
- **Addresses NFR-M1**: Add languages via config only (no code changes)
- **Benefits**:
  - Scalable to 20+ languages without code bloat
  - User-customizable (override node types, penalties)
  - Easier to test (mock configs)
  - Single source of truth (AST extractor + chunker use same config)

**Alternatives Considered:**
- **Alternative 1**: Hardcoded if/elif chains per language (current ast.py approach)
  - **Why Not Chosen**: Doesn't scale, requires code changes per language, ~60 lines per language
- **Alternative 2**: Plugin system with per-language Python modules
  - **Why Not Chosen**: Over-engineered, increases complexity, harder to maintain

**Trade-offs:**
- **Pros**: Scalability, maintainability, testability
- **Cons**: Requires config validation on startup (catches invalid node types)

---

#### Decision 2: Two-Pronged Approach (AST Chunking + Import Penalty)

**Decision:** Implement both AST-aware chunking (primary fix) AND import ranking penalty (secondary fix).

**Rationale:**
- **Addresses FR-001**: AST-aware chunking at function/class boundaries
- **Addresses FR-002**: Import penalty mechanism
- **Addresses Goal 1**: Improve code discovery relevance (Relevance@5: 60% → 90%)
- **Benefits**:
  - AST chunking prevents mid-function splits (precision)
  - Import penalty demotes low-value chunks (relevance)
  - Combined effect: Implementations naturally rank higher

**Alternatives Considered:**
- **Alternative 1**: AST chunking only (no penalty)
  - **Why Not Chosen**: Import files would still rank high (token density advantage)
- **Alternative 2**: Import penalty only (no AST chunking)
  - **Why Not Chosen**: Doesn't fix line-based chunking issues (mid-function splits)

**Trade-offs:**
- **Pros**: Comprehensive fix, addresses root cause + symptom
- **Cons**: Two mechanisms to maintain (acceptable complexity)

---

#### Decision 3: Tree-sitter for AST Parsing

**Decision:** Use Tree-sitter library for AST parsing (reuse existing infrastructure).

**Rationale:**
- **Addresses FR-001**: AST parsing requirement
- **Infrastructure Reuse**: prAxIs OS already uses Tree-sitter in `ast.py` for symbol extraction
- **Benefits**:
  - Proven, fast, incremental parser
  - Supports 40+ languages (via grammars)
  - Shared parser infrastructure (AST extractor + chunker)
  - No new dependencies (already installed)

**Alternatives Considered:**
- **Alternative 1**: Language-specific native parsers (ast module for Python, TypeScript compiler API)
  - **Why Not Chosen**: Requires different parser per language, doesn't scale
- **Alternative 2**: Regex-based chunking
  - **Why Not Chosen**: Fragile, doesn't handle nested structures, not true AST parsing

**Trade-offs:**
- **Pros**: Proven, fast, language-agnostic, infrastructure reuse
- **Cons**: Parsing 2-3x slower than line-based (acceptable one-time cost at index time)

---

#### Decision 4: Index-Time Chunking (Not Query-Time)

**Decision:** Perform AST parsing and chunking at index build time, not at search query time.

**Rationale:**
- **Addresses NFR-P1**: Search query latency <200ms p95
- **Addresses FR-005**: Graceful fallback (index stores chunks, not raw code)
- **Benefits**:
  - Zero query-time overhead (parsing already done)
  - Fallback to line-based chunks transparent to search
  - Index rebuild is one-time cost (<10 minutes for 100K LOC)

**Alternatives Considered:**
- **Alternative 1**: Query-time chunking (parse on every search)
  - **Why Not Chosen**: Unacceptable latency (500+ms per query), violates NFR-P1

**Trade-offs:**
- **Pros**: Fast queries, graceful degradation
- **Cons**: Index rebuild required when changing chunking strategy (acceptable)

---

#### Decision 5: Graceful Fallback to Line-Based Chunking

**Decision:** When AST parsing fails, fall back to existing line-based chunking (200 lines, 20-line overlap).

**Rationale:**
- **Addresses FR-005**: Graceful fallback requirement
- **Addresses NFR-R1**: Graceful degradation
- **Benefits**:
  - Search remains operational even if AST parsing fails
  - No user-facing errors for parse failures
  - Health check reports degraded status (not failure)

**Alternatives Considered:**
- **Alternative 1**: Fail index build on parse errors
  - **Why Not Chosen**: Too brittle, violates operational requirements
- **Alternative 2**: Skip failed files (don't index at all)
  - **Why Not Chosen**: Degrades search coverage, worse than line-based fallback

**Trade-offs:**
- **Pros**: Operational resilience, no user-facing failures
- **Cons**: Mixed chunk quality (AST + line-based), acceptable for edge cases

---

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| **FR-001**: AST-Aware Chunking | UniversalASTChunker + Tree-sitter | Chunks at function/class boundaries using Tree-sitter AST parsing |
| **FR-002**: Import Penalty | CodeChunk.import_penalty + RRF ranking | Calculates import_ratio, applies 0.3 penalty multiplier in search ranking |
| **FR-003**: Token-Based Sizing | UniversalASTChunker._estimate_tokens() | Targets 500 tokens/chunk, splits at split_boundary_nodes if needed |
| **FR-004**: Config-Driven Languages | mcp.yaml language_configs | Node types defined in config, no code changes per language |
| **FR-005**: Graceful Fallback | SemanticIndex._chunk_file() fallback | Falls back to line-based chunking on AST parse failure |
| **FR-006**: Index Rebuild | SemanticIndex.build() | Rebuilds index with AST chunking, replaces line-based chunks |
| **FR-007**: Config Rollback | mcp.yaml chunking_strategy flag | Set `chunking_strategy: "line"` to rollback, rebuild in <5 minutes |
| **FR-008**: Health Check Integration | CodeIndex.components registry | AST chunker registered as component, reports operational/degraded/fallback status |
| **FR-009**: Import Chunk Grouping | UniversalASTChunker._chunk_imports() | Groups consecutive imports into single chunk with chunk_type="import" |
| **FR-010**: Multi-Language Consistency | UniversalASTChunker (language-agnostic) | Same algorithm for all languages, behavior controlled via config |
| **NFR-P1**: Search Latency <200ms | Index-time chunking | Parsing done at index time, zero query-time overhead |
| **NFR-P2**: Index Build <10 min | Parallel processing, Tree-sitter efficiency | Multi-core parsing, 300-500 files/second acceptable |
| **NFR-P3**: Penalty Overhead <1ms | Simple import_ratio calculation | O(1) penalty application in RRF ranking step |
| **NFR-R1**: Graceful Degradation | Fallback to line-based chunking | Parse failures logged, fallback activated, search continues |
| **NFR-R2**: Rollback <5 minutes | Config-based rollback | Change config, rebuild index (parallel processing) |
| **NFR-R3**: Health Monitoring | Cascading Health Check Architecture | AST chunker component reports health, metrics, diagnostics |
| **NFR-M1**: Config-Only Languages | mcp.yaml language_configs | Zero code changes to add language |
| **NFR-SC1**: Multi-Repo Support | Partition-agnostic chunking | AST chunking applies across all partitions (primary, instrumentors) |
| **NFR-C2**: Existing RAG Integration | SemanticIndex API compatibility | No breaking changes, extends existing _chunk_file() method |

---

### 1.5 Technology Stack

**Programming Language:**
- Python 3.10+ (prAxIs OS standard)

**AST Parsing:**
- **Tree-sitter**: Fast, incremental parser with 40+ language grammars
- **py-tree-sitter**: Python bindings for Tree-sitter
- **tree-sitter-language-pack**: Pre-built language grammars (Python, TypeScript, Go, etc.)

**Embedding & Search:**
- **CodeBERT** (microsoft/codebert-base): Pre-trained code embeddings (768-dimensional)
- **LanceDB**: Columnar vector database for embeddings + FTS
- **Reciprocal Rank Fusion (RRF)**: Combines vector + FTS search results

**Configuration:**
- **YAML** (mcp.yaml): Unified config for language node types, chunking parameters, penalties

**Health Monitoring:**
- **Cascading Health Check Architecture**: Component-level health reporting, graceful degradation

**Testing:**
- **pytest**: Unit and integration testing
- **Human evaluation**: Relevance@5 metric (100 query sample)

---

### 1.6 Deployment Architecture

**Deployment Model:** Local embedded system (no external services)

**Components:**
- **prAxIs OS MCP Server**: Hosts RAG subsystem, runs locally on developer machine
- **LanceDB Indexes**: Local disk storage (`.praxis-os/.cache/indexes/code`)
- **Configuration**: Local file (`mcp.yaml`)

**Deployment Flow:**
1. Update `mcp.yaml` with `chunking_strategy: "ast"`
2. Delete old index: `rm -rf .praxis-os/.cache/indexes/code`
3. Restart MCP server: `mcp-server restart`
4. Index rebuild automatic (1-2 minutes for 100K LOC)

**Rollback Flow:**
1. Update `mcp.yaml` with `chunking_strategy: "line"`
2. Preserve AST index: `mv .praxis-os/.cache/indexes/code{,.ast-backup}`
3. Restart MCP server
4. Index rebuild with line-based chunking (<5 minutes)

---

### 1.7 Integration Points

**Upstream Integrations:**
- **mcp.yaml**: AST chunker reads `language_configs` section
- **ASTExtractor**: Shares Tree-sitter parser instances (infrastructure reuse)
- **Tree-sitter Language Pack**: Provides language grammars

**Downstream Integrations:**
- **SemanticIndex**: Calls AST chunker during `build()` method
- **LanceDB**: Stores chunks with metadata (chunk_type, import_penalty, symbols)
- **Search Ranking**: Applies import penalty in RRF fusion step
- **Health Checks**: Reports AST chunker status via `pos_search_project` tool

**No Breaking Changes:**
- SemanticIndex API unchanged (internal implementation detail)
- Search queries work identically (transparent to users)
- Line-based fallback preserves compatibility

---

## 2. Component Design

This section defines each component identified in the architecture, specifying responsibilities, public interfaces, dependencies, and internal structure.

---

### 2.1 Component: UniversalASTChunker

**Purpose:** Language-agnostic AST-aware code chunker that parses source code using Tree-sitter and creates chunks at function/class boundaries, applying import penalties.

**Responsibilities:**
- Parse source code files using Tree-sitter for configured languages
- Chunk code at AST boundaries (function definitions, class definitions)
- Group consecutive import statements into single chunks
- Calculate import ratio for each chunk (import_lines / total_lines)
- Apply configurable import penalty multiplier to import-heavy chunks
- Estimate token counts for CodeBERT compatibility (target: 500 tokens)
- Split oversized chunks at logical boundaries (if/try/for statements)
- Handle parse failures gracefully (log and return empty list)

**Requirements Satisfied:**
- **FR-001**: AST-Aware Code Chunking - Chunks at function/class boundaries using Tree-sitter
- **FR-002**: Import Penalty Mechanism - Calculates import_ratio and applies penalty multiplier
- **FR-003**: Token-Based Chunk Sizing - Targets 500 tokens per chunk
- **FR-004**: Configuration-Driven Language Support - Reads node types from mcp.yaml
- **FR-009**: Import Chunk Grouping - Groups consecutive imports into single chunk

**Public Interface:**
```python
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CodeChunk:
    """Semantic code chunk (function, class, or imports)."""
    content: str                # Chunk text content
    file_path: Path             # Source file path
    start_line: int             # 1-indexed start line
    end_line: int               # 1-indexed end line
    chunk_type: str             # "function", "class", "import", "module"
    symbols: List[str]          # Function/class names in chunk
    import_ratio: float         # 0.0-1.0 (percentage of import lines)
    import_penalty: float       # 0.3-1.0 (ranking multiplier)
    token_count: int            # Estimated tokens (for CodeBERT)

class UniversalASTChunker:
    """Language-agnostic AST chunker using unified config."""
    
    def __init__(self, language: str, config: dict, base_path: Path):
        """Initialize chunker for a specific language.
        
        Args:
            language: Language name (e.g., "python", "typescript")
            config: Full code index config from mcp.yaml
            base_path: Base path for resolving relative paths
        """
        pass
    
    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a code file at AST boundaries.
        
        Returns chunks with complete context (no mid-function splits).
        On parse failure, returns empty list (fallback handled by caller).
        """
        pass
```

**Dependencies:**
- **Requires**:
  - `mcp.yaml` config (language_configs section)
  - Tree-sitter parser (from `tree-sitter-language-pack`)
  - ASTExtractor (shared parser infrastructure)
- **Provides**:
  - List[CodeChunk] with complete semantic units
  - Import penalty metadata for search ranking

**Internal Structure:**
- `_chunk_imports(nodes, code, file_path) -> CodeChunk`: Groups imports into single chunk
- `_chunk_definition(node, code, file_path) -> CodeChunk`: Chunks function/class as complete unit
- `_split_large_chunk(node, code, file_path) -> List[CodeChunk]`: Splits oversized chunks at boundaries
- `_estimate_tokens(content) -> int`: Estimates token count (4 chars ≈ 1 token)
- `_calculate_import_ratio(chunk) -> float`: Calculates percentage of import lines

**Error Handling:**
- **Parse failure** → Log warning with file path and error, return empty list
- **Missing language config** → Log warning, use default node types (function_definition, class_definition)
- **Token overflow (>514)** → Split at split_boundary_nodes, log warning if can't split

---

### 2.2 Component: ASTExtractor (Refactored)

**Purpose:** Extract AST nodes, symbols, and relationships from source code using Tree-sitter for graph traversal and code intelligence.

**Responsibilities:**
- Read language-specific node types from `mcp.yaml` (instead of hardcoded if/elif chains)
- Parse source code into AST using Tree-sitter
- Extract significant nodes (functions, classes, if statements, etc.)
- Extract symbols (function/class names) for graph index
- Extract call relationships for graph traversal
- Provide shared Tree-sitter parser instances to AST chunker

**Requirements Satisfied:**
- **FR-004**: Configuration-Driven Language Support - Reads node types from config
- **NFR-M1**: Configuration-Only Languages - Removes ~60 lines of if/elif chains per language

**Public Interface:**
```python
class ASTExtractor:
    """Extract AST nodes, symbols, and relationships from source code."""
    
    def __init__(self, languages: List[str], base_path: Path, config: dict):
        """Initialize AST extractor.
        
        Args:
            languages: List of language names (e.g., ["python", "typescript"])
            base_path: Base path for resolving relative paths
            config: Language configs from mcp.yaml (indexes.code.language_configs)
        """
        pass
    
    def _get_significant_node_types(self, language: str) -> set:
        """Get significant AST node types for a language.
        
        OLD: 40 lines of if/elif chains
        NEW: 5 lines reading from config!
        """
        pass
    
    def _get_symbol_node_types(self, language: str) -> set:
        """Get symbol node types for a language (functions, classes)."""
        pass
    
    def _get_call_node_types(self, language: str) -> set:
        """Get call node types for a language (function calls, method calls)."""
        pass
    
    def ensure_parser(self, language: str) -> None:
        """Ensure Tree-sitter parser is loaded for language."""
        pass
    
    @property
    def _parsers(self) -> Dict[str, Any]:
        """Access to shared Tree-sitter parser instances."""
        pass
```

**Dependencies:**
- **Requires**:
  - `mcp.yaml` config (language_configs section)
  - Tree-sitter language grammars (from `tree-sitter-language-pack`)
- **Provides**:
  - AST nodes for GraphIndex
  - Symbols and relationships for graph traversal
  - Shared Tree-sitter parser instances for AST chunker

**Changes from Original:**
- Remove hardcoded if/elif chains (~60 lines per language)
- Add config reading (~15 lines for all languages)
- Net reduction: ~45 lines per language
- Easier to test (mock configs)
- Easier to extend (add language in config)

**Error Handling:**
- **Missing language config** → Log warning, use default node types (graceful degradation)
- **Parse failure** → Log error, return empty AST (handled by caller)
- **Invalid node types** → Log warning, filter out invalid types

---

### 2.3 Component: SemanticIndex (Modified)

**Purpose:** Index code chunks with CodeBERT embeddings and FTS for semantic search, applying import penalties in ranking.

**Responsibilities:**
- Chunk source code files (using AST chunker or line-based fallback)
- Generate CodeBERT embeddings for each chunk
- Store chunks in LanceDB with metadata (chunk_type, import_penalty, symbols)
- Build FTS index for keyword search
- Execute hybrid search (vector + FTS + RRF fusion)
- Apply import penalties in final ranking
- Handle health checks (report operational/degraded status)

**Requirements Satisfied:**
- **FR-001**: AST-Aware Chunking - Integrates UniversalASTChunker
- **FR-002**: Import Penalty - Applies penalty in RRF ranking
- **FR-005**: Graceful Fallback - Falls back to line-based chunking on parse failure
- **FR-006**: Index Rebuild - Supports rebuilding with AST chunking
- **NFR-P1**: Search Latency <200ms - Index-time chunking, zero query overhead

**Public Interface:**
```python
class SemanticIndex:
    """Semantic code search using CodeBERT + FTS + RRF."""
    
    def build(self, source_paths: List[Path], force: bool = False) -> None:
        """Build code index with AST-aware chunking.
        
        Args:
            source_paths: List of directories/files to index
            force: If True, rebuild from scratch (delete existing)
        """
        pass
    
    def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single code file.
        
        Strategy:
        1. Try AST-aware chunking (UniversalASTChunker)
        2. On failure, fall back to line-based chunking
        3. Log fallback activation for health monitoring
        """
        pass
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Execute hybrid search with import penalties.
        
        Steps:
        1. Vector search (CodeBERT embeddings)
        2. FTS search (keyword matching)
        3. RRF fusion (combine results)
        4. Apply import penalties: final_score = base_score * import_penalty
        5. Return top N results
        """
        pass
    
    def health_check(self) -> HealthStatus:
        """Report index health (operational/degraded/fallback).
        
        Returns:
            HealthStatus with metrics: chunk_count, fallback_count, avg_token_size
        """
        pass
```

**Dependencies:**
- **Requires**:
  - UniversalASTChunker (for AST chunking)
  - CodeBERT model (for embeddings)
  - LanceDB (for storage)
  - RRF implementation (for ranking)
- **Provides**:
  - Semantic search API for `pos_search_project` tool
  - Health status for Cascading Health Check Architecture

**Changes from Original:**
- Replace `_chunk_file()` implementation to use AST chunker
- Add try/except for AST chunking with fallback to line-based
- Add import penalty application in `search()` method (RRF fusion step)
- Track fallback count for health monitoring

**Error Handling:**
- **AST chunking failure** → Fall back to line-based chunking, log warning
- **Parse failure** → Use line-based chunks (200 lines, 20-line overlap)
- **Embedding failure** → Log error, skip chunk (don't block index build)
- **Search failure** → Return empty results with error message

---

### 2.4 Component: mcp.yaml Configuration

**Purpose:** Centralized configuration for language-specific AST node types, chunking parameters, and import penalties.

**Responsibilities:**
- Define language-specific node types (import_nodes, definition_nodes, split_boundary_nodes)
- Specify import penalty multiplier per language (default: 0.3)
- Configure chunking strategy feature flag ("ast" or "line")
- Define vector/FTS parameters (chunk_size: 500, chunk_overlap: 50)
- Validate config on startup (detect invalid node types)

**Requirements Satisfied:**
- **FR-004**: Configuration-Driven Language Support - Single source of truth for node types
- **FR-007**: Configuration-Based Rollback - Set chunking_strategy: "line" for rollback
- **NFR-M1**: Configuration-Only Languages - Add language via config (no code changes)

**Configuration Schema:**
```yaml
indexes:
  code:
    source_paths: ["ouroboros/"]
    languages: ["python", "typescript", "go"]
    
    # Chunking strategy: "ast" (AST-aware) or "line" (fallback)
    chunking_strategy: "ast"  # Feature flag for rollback
    
    vector:
      model: "microsoft/codebert-base"
      chunk_size: 500      # Target tokens per chunk (CodeBERT limit: 514)
      chunk_overlap: 50    # Overlap tokens between chunks
      dimension: 768       # CodeBERT embedding dimension
    
    fts:
      enabled: true
    
    # Language-specific node type mappings
    language_configs:
      python:
        # AST node types (used by ASTExtractor)
        significant_nodes:
          - function_definition
          - async_function_definition
          - class_definition
          - if_statement
          - for_statement
          - try_statement
          - import_statement
          - import_from_statement
        
        symbol_nodes:
          - function_definition
          - async_function_definition
          - class_definition
        
        call_nodes:
          - call
          - attribute
        
        # Chunking-specific rules (used by UniversalASTChunker)
        chunking:
          import_nodes:
            - import_statement
            - import_from_statement
            - future_import_statement
          
          definition_nodes:
            - function_definition
            - async_function_definition
            - class_definition
            - decorated_definition
          
          split_boundary_nodes:
            - if_statement
            - for_statement
            - while_statement
            - try_statement
            - with_statement
          
          import_penalty: 0.3  # 70% score reduction for import-heavy chunks
      
      typescript:
        # ... similar structure ...
      
      go:
        # ... similar structure ...
```

**Dependencies:**
- **Requires**: None (configuration file)
- **Provides**: Configuration data to ASTExtractor, UniversalASTChunker, SemanticIndex

**Validation Rules:**
- Language names must match Tree-sitter grammar names
- Node types must be valid for the language's Tree-sitter grammar
- Import penalty must be in range [0.0, 1.0]
- Chunk size must be ≤514 (CodeBERT limit)

**Error Handling:**
- **Invalid node type** → Log warning, filter out invalid type, continue with valid types
- **Missing language config** → Use default node types (function_definition, class_definition)
- **Invalid penalty value** → Use default (0.3)

---

### 2.5 Component Interactions

**Interaction Diagram:**

```
Index Build Time:
─────────────────

SemanticIndex.build()
    │
    ├─► For each source file:
    │       │
    │       ├─► _chunk_file(file_path)
    │       │       │
    │       │       ├─► Try: UniversalASTChunker.chunk_file(file_path)
    │       │       │           │
    │       │       │           ├─► Read language_configs from mcp.yaml
    │       │       │           │
    │       │       │           ├─► Get parser from ASTExtractor._parsers
    │       │       │           │
    │       │       │           ├─► Parse file with Tree-sitter
    │       │       │           │
    │       │       │           ├─► Chunk at function/class boundaries
    │       │       │           │
    │       │       │           ├─► Calculate import_ratio per chunk
    │       │       │           │
    │       │       │           └─► Return List[CodeChunk]
    │       │       │
    │       │       └─► Except: Fall back to line-based chunking
    │       │
    │       ├─► Generate CodeBERT embeddings
    │       │
    │       └─► Store in LanceDB (with metadata: chunk_type, import_penalty, symbols)
    │
    └─► Build FTS index


Query Time:
───────────

pos_search_project(action="search_code", query="...")
    │
    └─► SemanticIndex.search(query, n_results=5)
            │
            ├─► Vector search (CodeBERT embeddings)
            │
            ├─► FTS search (keyword matching)
            │
            ├─► RRF fusion (combine results)
            │
            ├─► Apply import penalties:
            │       For each result:
            │           if result.chunk_type == "import" and result.import_ratio > 0.5:
            │               result.score *= result.import_penalty  # Reduce by 70%
            │
            └─► Return top N results (sorted by final_score)
```

**Component Interaction Table:**

| From | To | Method/API | Purpose |
|------|----|-----------|---------| 
| SemanticIndex | UniversalASTChunker | `chunk_file(file_path)` | Get AST-aware chunks for file |
| UniversalASTChunker | mcp.yaml | Config read | Get language node types and penalties |
| UniversalASTChunker | ASTExtractor | `_parsers[language]` | Get shared Tree-sitter parser |
| SemanticIndex | LanceDB | `.add(chunks)` | Store chunks with metadata |
| pos_search_project | SemanticIndex | `.search(query)` | Execute semantic search |
| SemanticIndex | CodeBERT | `.encode(text)` | Generate embeddings |
| SemanticIndex | RRF | `.fuse(vector_results, fts_results)` | Combine search results |

---

### 2.6 Module Organization

**Directory Structure:**
```
ouroboros/subsystems/rag/code/
├── semantic/
│   ├── __init__.py
│   ├── semantic.py           # SemanticIndex (modified)
│   └── ast_chunker.py        # UniversalASTChunker (NEW)
│
├── graph/
│   ├── __init__.py
│   ├── container.py          # GraphIndex
│   └── ast.py                # ASTExtractor (refactored)
│
└── __init__.py

.praxis-os/config/
└── mcp.yaml                   # Unified configuration (extended)

tests/
├── test_ast_chunker.py        # Unit tests for UniversalASTChunker
├── test_semantic_index.py     # Integration tests for SemanticIndex
└── test_import_penalty.py     # Tests for import penalty application
```

**Dependency Rules:**
- **No circular imports**: SemanticIndex → UniversalASTChunker → ASTExtractor (one-way)
- **Config-driven**: Components read from mcp.yaml (no hardcoded constants)
- **Shared infrastructure**: ASTExtractor provides parsers, UniversalASTChunker uses them
- **Graceful degradation**: Each component handles failures locally (log and fallback)

**Module Responsibilities:**
- `semantic.py`: Orchestrates chunking, embedding, indexing, search
- `ast_chunker.py`: Pure AST logic (no embedding/indexing concerns)
- `ast.py`: Pure AST extraction (no chunking concerns)
- `mcp.yaml`: Configuration only (no logic)

---

## 3. API Design

This section defines the public interfaces, internal APIs, and data contracts for AST-aware code chunking. **Note**: This feature has no new HTTP/REST endpoints - it enhances existing internal APIs within the RAG subsystem.

---

### 3.1 Public Tool API (MCP)

The AST-aware chunking feature is transparent to end users. The existing `pos_search_project` tool API remains unchanged, but internal behavior improves (better ranking).

**Tool:** `pos_search_project`

**Action:** `search_code`

**API Signature:**
```python
pos_search_project(
    action="search_code",
    query="EventsAPI list_events filters",  # Natural language query
    n_results=5,                             # Number of results (default: 5)
    method="hybrid"                          # Search method (hybrid/vector/fts)
)
```

**Response Format** (unchanged):
```json
{
  "status": "success",
  "action": "search_code",
  "results": [
    {
      "content": "<code chunk text>",
      "file_path": "api/events.py",
      "start_line": 181,
      "end_line": 250,
      "relevance_score": 0.8423,
      "chunk_type": "function",          // NEW metadata
      "symbols": ["list_events"],        // NEW metadata
      "import_penalty": 1.0              // NEW metadata (1.0 = no penalty)
    }
  ],
  "count": 5
}
```

**Behavioral Changes:**
- **Before**: Import files (`__init__.py`) rank #1-3, implementations #4+
- **After**: Implementations rank #1-2, imports #5+
- **Latency**: No regression (<200ms p95 maintained)
- **Fallback**: Gracefully degrades to line-based chunking on AST failures

---

### 3.2 Internal APIs

#### 3.2.1 UniversalASTChunker Interface

**Primary API:**
```python
class UniversalASTChunker:
    def __init__(self, language: str, config: dict, base_path: Path):
        """Initialize AST chunker for a language.
        
        Args:
            language: Language name (e.g., "python", "typescript", "go")
            config: Full code index config from mcp.yaml (indexes.code)
            base_path: Base path for resolving relative file paths
        
        Raises:
            ValueError: If language not supported (no Tree-sitter grammar)
            ConfigError: If config is invalid (handled gracefully with defaults)
        """
        pass
    
    def chunk_file(self, file_path: Path) -> List[CodeChunk]:
        """Chunk a single code file at AST boundaries.
        
        Args:
            file_path: Path to source file (absolute or relative to base_path)
        
        Returns:
            List of CodeChunk objects with complete semantic units.
            Returns empty list on parse failure (caller handles fallback).
        
        Raises:
            None (errors logged, empty list returned for graceful degradation)
        
        Performance:
            - 300-500 files/second (2-3x slower than line-based)
            - Acceptable one-time cost at index build time
        """
        pass
```

**Data Model:**
```python
@dataclass
class CodeChunk:
    """Semantic code chunk with metadata."""
    content: str                # Full text of chunk
    file_path: Path             # Source file (for traceability)
    start_line: int             # 1-indexed start line (inclusive)
    end_line: int               # 1-indexed end line (inclusive)
    chunk_type: str             # "function" | "class" | "import" | "module"
    symbols: List[str]          # Function/class names (empty for imports)
    import_ratio: float         # 0.0-1.0 (0.0=no imports, 1.0=all imports)
    import_penalty: float       # 0.3-1.0 (penalty multiplier, 0.3=70% reduction)
    token_count: int            # Estimated tokens (for CodeBERT, target: 500)
```

**Contract:**
- Chunks are complete semantic units (no mid-function splits)
- Import chunks have `chunk_type="import"` and `import_ratio=1.0`
- Function/class chunks have `chunk_type="function"` or `"class"`
- Token count targets 500 (±20% tolerance: 400-600)
- Oversized chunks split at split_boundary_nodes (if/try/for)
- Parse failures return empty list (no exceptions thrown)

---

#### 3.2.2 SemanticIndex Interface (Modified)

**Modified Method:**
```python
class SemanticIndex:
    def _chunk_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Chunk a single code file (with AST fallback).
        
        Strategy (NEW):
        1. Try AST-aware chunking via UniversalASTChunker
        2. On failure, fall back to line-based chunking
        3. Log fallback activation for health monitoring
        
        Args:
            file_path: Path to source file
        
        Returns:
            List of chunk dictionaries with metadata:
            - content: str
            - file_path: str
            - start_line: int
            - end_line: int
            - chunk_type: str (NEW)
            - symbols: List[str] (NEW)
            - import_ratio: float (NEW)
            - import_penalty: float (NEW)
            - token_count: int (NEW)
        
        Performance:
            - AST: 300-500 files/second
            - Fallback (line-based): 1000 files/second
            - Mixed mode: depends on failure rate
        """
        pass
```

**New Method:**
```python
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Execute hybrid search with import penalties (NEW logic).
        
        Steps (MODIFIED):
        1. Vector search (CodeBERT embeddings)
        2. FTS search (keyword matching)
        3. RRF fusion (combine vector + FTS results)
        4. **Apply import penalties** (NEW):
               if chunk.chunk_type == "import" and chunk.import_ratio > 0.5:
                   chunk.score *= chunk.import_penalty  # Reduce by 70%
        5. Sort by final_score DESC
        6. Return top N results
        
        Args:
            query: Natural language search query
            n_results: Number of results to return (default: 5)
        
        Returns:
            List of result dictionaries sorted by relevance
        
        Performance:
            - Latency: <200ms p95 (no regression)
            - Penalty overhead: <1ms (O(n) where n=results)
        """
        pass
```

---

#### 3.2.3 ASTExtractor Interface (Refactored)

**Refactored Method:**
```python
class ASTExtractor:
    def _get_significant_node_types(self, language: str) -> set:
        """Get significant AST node types for a language (config-driven).
        
        OLD Implementation:
            40 lines of if/elif chains per language
            if language == "python":
                return {"function_definition", "class_definition", ...}
            elif language == "typescript":
                return {"function_declaration", "class_declaration", ...}
            ...
        
        NEW Implementation:
            5 lines reading from config for ALL languages
            lang_config = self.lang_configs.get(language, {})
            if "significant_nodes" in lang_config:
                return set(lang_config["significant_nodes"])
            return {"function_definition", "class_definition"}  # Fallback
        
        Args:
            language: Language name (e.g., "python")
        
        Returns:
            Set of AST node type strings (e.g., {"function_definition", ...})
        
        Benefits:
            - Scalable: Add language via config, not code
            - Testable: Mock configs in unit tests
            - User-customizable: Override in mcp.yaml
        """
        pass
```

---

###3.3 Configuration API (mcp.yaml)

**Schema:**
```yaml
indexes:
  code:
    # Existing fields (unchanged)
    source_paths: ["ouroboros/"]
    languages: ["python", "typescript", "go"]
    
    vector:
      model: "microsoft/codebert-base"
      chunk_size: 500         # NEW semantic meaning: target tokens (not lines)
      chunk_overlap: 50       # NEW semantic meaning: tokens (not lines)
      dimension: 768
    
    fts:
      enabled: true
    
    # NEW: Chunking strategy feature flag
    chunking_strategy: "ast"   # "ast" or "line" (default: "ast")
    
    # NEW: Language-specific node type mappings
    language_configs:
      python:
        # AST extraction (used by ASTExtractor)
        significant_nodes: ["function_definition", "class_definition", ...]
        symbol_nodes: ["function_definition", "class_definition"]
        call_nodes: ["call", "attribute"]
        
        # AST chunking (used by UniversalASTChunker)
        chunking:
          import_nodes: ["import_statement", "import_from_statement"]
          definition_nodes: ["function_definition", "class_definition"]
          split_boundary_nodes: ["if_statement", "for_statement", ...]
          import_penalty: 0.3    # 0.0-1.0 (0.3 = 70% score reduction)
```

**Validation Rules:**
- `chunking_strategy`: Must be "ast" or "line"
- `language_configs.{lang}.chunking.import_penalty`: Must be 0.0-1.0
- `vector.chunk_size`: Must be ≤514 (CodeBERT limit)
- Node type strings: Must match Tree-sitter grammar for language

**Error Handling:**
- Invalid `chunking_strategy`: Log warning, default to "ast"
- Invalid `import_penalty`: Log warning, default to 0.3
- Missing `language_configs.{lang}`: Log warning, use default node types
- Invalid node type: Log warning, filter out invalid, continue with valid

---

### 3.4 Health Check API

**Interface:**
```python
def health_check() -> HealthStatus:
    """Report AST chunker health status.
    
    Returns:
        HealthStatus object with:
        - healthy: bool (operational/degraded/failure)
        - message: str (human-readable status)
        - details: Dict with metrics:
            - chunk_count: int (total chunks indexed)
            - fallback_count: int (files using line-based fallback)
            - fallback_rate: float (fallback_count / total_files)
            - avg_token_size: float (average chunk tokens)
            - ast_enabled: bool (chunking_strategy == "ast")
    
    Status Interpretation:
        - healthy=True: AST chunking operational, fallback_rate <25%
        - healthy=False (degraded): Fallback_rate 25-75%
        - healthy=False (failure): Fallback_rate >75% or AST disabled
    """
    pass
```

**Example Response:**
```json
{
  "healthy": true,
  "message": "AST chunker operational (237 chunks, 12 fallbacks, 4.8% fallback rate)",
  "details": {
    "chunk_count": 237,
    "fallback_count": 12,
    "fallback_rate": 0.048,
    "avg_token_size": 487,
    "ast_enabled": true,
    "languages": {
      "python": {"chunks": 180, "fallbacks": 5},
      "typescript": {"chunks": 45, "fallbacks": 7},
      "go": {"chunks": 12, "fallbacks": 0}
    }
  }
}
```

---

### 3.5 Error Handling

**Error Categories:**

**1. Parse Failures (Graceful)**
```python
# AST parse failure
{
  "error_type": "ParseError",
  "severity": "WARNING",  # Not fatal
  "message": "Failed to parse {file_path}: {error}",
  "action": "Falling back to line-based chunking",
  "file_path": "problematic_file.py",
  "language": "python"
}
```
**Handling**: Log warning, return empty list, SemanticIndex falls back to line-based

**2. Config Errors (Graceful)**
```python
# Invalid config
{
  "error_type": "ConfigError",
  "severity": "WARNING",
  "message": "Invalid node type '{type}' for language '{lang}'",
  "action": "Using default node types",
  "lang": "python",
  "invalid_type": "nonexistent_node"
}
```
**Handling**: Log warning, use default node types, continue operation

**3. Token Overflow (Graceful)**
```python
# Chunk exceeds CodeBERT limit
{
  "error_type": "TokenOverflow",
  "severity": "WARNING",
  "message": "Chunk exceeds 514 tokens ({count}), splitting at boundaries",
  "action": "Splitting at split_boundary_nodes",
  "file_path": "large_file.py",
  "token_count": 620,
  "function_name": "very_long_function"
}
```
**Handling**: Log warning, split at if/try/for statements, continue

**4. Fatal Errors (Rare)**
```python
# Missing Tree-sitter grammar
{
  "error_type": "MissingGrammar",
  "severity": "ERROR",
  "message": "Tree-sitter grammar not found for language '{lang}'",
  "action": "Language not supported, falling back to line-based for all files",
  "lang": "rust"
}
```
**Handling**: Log error, disable AST chunking for that language, fall back to line-based

**Error Response Format** (Internal):
All errors logged to prAxIs OS logger with structured format:
```python
logger.warning(
    "AST parse failure",
    extra={
        "file_path": file_path,
        "language": language,
        "error": str(error),
        "action": "fallback_to_line_based"
    }
)
```

**No User-Facing Errors**: All failures handled gracefully with fallback, users see normal search results (may have slightly lower quality for failed files).

---

## 4. Data Models

This section defines the data structures, schemas, and relationships for AST-aware code chunking.

---

### 4.1 Domain Models

**CodeChunk (Primary Domain Model):**
```python
from dataclasses import dataclass
from pathlib import Path
from typing import List

@dataclass
class CodeChunk:
    """Semantic code chunk with metadata.
    
    Represents a single unit of code (function, class, or import group)
    extracted via AST-aware chunking.
    """
    content: str                # Full text of chunk
    file_path: Path             # Source file (for traceability)
    start_line: int             # 1-indexed start line (inclusive)
    end_line: int               # 1-indexed end line (inclusive)
    chunk_type: str             # "function" | "class" | "import" | "module"
    symbols: List[str]          # Function/class names (empty for imports)
    import_ratio: float         # 0.0-1.0 (0.0=no imports, 1.0=all imports)
    import_penalty: float       # 0.3-1.0 (penalty multiplier for ranking)
    token_count: int            # Estimated tokens (for CodeBERT)
    
    def __post_init__(self):
        """Validate chunk constraints."""
        assert 0.0 <= self.import_ratio <= 1.0, "import_ratio must be 0-1"
        assert 0.0 <= self.import_penalty <= 1.0, "import_penalty must be 0-1"
        assert self.token_count <= 514, "token_count exceeds CodeBERT limit"
        assert self.start_line <= self.end_line, "Invalid line range"
```

**Business Rules:**
- Chunks are immutable (dataclass frozen=False for flexibility, but not modified after creation)
- Token count must not exceed 514 (CodeBERT hard limit)
- Import ratio and penalty are stored for transparency (not recalculated at query time)
- Chunk type determines search ranking behavior (imports deprioritized)
- Symbols list enables metadata filtering (e.g., "find chunks containing function X")

---

**LanguageConfig (Configuration Model):**
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LanguageConfig:
    """Language-specific AST node configuration.
    
    Loaded from mcp.yaml for each supported language.
    """
    language: str                           # Language name (e.g., "python")
    import_nodes: List[str]                 # AST nodes for imports
    definition_nodes: List[str]             # AST nodes for functions/classes
    split_boundary_nodes: List[str]         # AST nodes for splitting large chunks
    import_penalty: float                   # Penalty multiplier (0.0-1.0)
    
    # Optional overrides
    target_chunk_size: Optional[int] = 500  # Target tokens per chunk
    chunk_overlap: Optional[int] = 50       # Overlap tokens
    
    def __post_init__(self):
        """Validate config."""
        assert 0.0 <= self.import_penalty <= 1.0, "import_penalty must be 0-1"
        assert self.target_chunk_size <= 514, "target_chunk_size exceeds limit"
```

**Business Rules:**
- Configuration is read-only at runtime (loaded once from mcp.yaml)
- Node type strings must match Tree-sitter grammar for language
- Invalid node types logged and filtered (graceful degradation)
- Default values provided for optional fields

---

### 4.2 Database Schema (LanceDB)

**Table: code_chunks**

LanceDB stores code chunks as a columnar table with vector embeddings and metadata.

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `content` | TEXT | Full chunk text | FTS |
| `file_path` | TEXT | Source file path | Yes |
| `start_line` | INT | Start line (1-indexed) | No |
| `end_line` | INT | End line (1-indexed) | No |
| `chunk_type` | TEXT | "function", "class", "import", "module" | Yes |
| `symbols` | LIST[TEXT] | Function/class names | No |
| `import_ratio` | FLOAT | 0.0-1.0 | No |
| `import_penalty` | FLOAT | 0.3-1.0 | No |
| `token_count` | INT | Estimated tokens | No |
| `vector` | ARRAY[768] | CodeBERT embedding | Vector Index |

**Indexes:**
- **Vector Index**: HNSW (Hierarchical Navigable Small World) for fast vector search
  - Dimension: 768 (CodeBERT)
  - Distance metric: Cosine similarity
  - Approximate search with high recall
- **FTS Index**: Full-text search on `content` column
  - Tokenizer: Standard (from LanceDB)
  - Case-insensitive
  - Stemming enabled
- **Metadata Index**: B-tree on `file_path` and `chunk_type` for filtering

**Schema Evolution:**
- **Before (Line-Based)**: Only `content`, `file_path`, `start_line`, `end_line`, `vector`
- **After (AST-Aware)**: Added `chunk_type`, `symbols`, `import_ratio`, `import_penalty`, `token_count`
- **Migration**: Full index rebuild required (delete `.praxis-os/.cache/indexes/code`, restart server)

---

### 4.3 Relationships

**Code Chunk → Source File (N:1)**
```
CodeChunk.file_path → File System
- One file produces multiple chunks
- Chunks retain source file path for traceability
- Deleting a file requires deleting all associated chunks
```

**Code Chunk → Language Config (N:1)**
```
CodeChunk (inferred language from file_path) → LanguageConfig
- Language detected from file extension (.py → python, .ts → typescript)
- Language config determines chunking behavior (import penalty, node types)
- Missing language config triggers fallback to line-based chunking
```

**Code Chunk → AST Node (1:1 or 1:N)**
```
CodeChunk ↔ AST Node (from GraphIndex)
- Function/class chunks map to single AST definition node
- Large function chunks may span multiple AST nodes (split at boundaries)
- Import chunks may group multiple AST import nodes
- **No foreign key**: Chunks and AST nodes stored in separate indexes (independent)
```

**Entity Relationship Diagram:**
```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Source Files  │       │   Code Chunks   │       │ Language Config │
│                 │       │  (LanceDB Table)│       │   (mcp.yaml)    │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ file_path (PK)  │◄──────┤ file_path (FK)  │       │ language (PK)   │
│ extension       │   N:1 │ content         │   N:1 │ import_nodes    │
│ size            │       │ chunk_type      ├──────►│ definition_nodes│
│ last_modified   │       │ symbols         │       │ import_penalty  │
└─────────────────┘       │ import_ratio    │       └─────────────────┘
                          │ import_penalty  │
                          │ token_count     │
                          │ vector          │
                          └─────────────────┘
                                  │
                                  │ 1:1 or 1:N
                                  ▼
                          ┌─────────────────┐
                          │   AST Nodes     │
                          │ (DuckDB Table)  │
                          ├─────────────────┤
                          │ id (PK)         │
                          │ file_path       │
                          │ node_type       │
                          │ start_line      │
                          │ end_line        │
                          └─────────────────┘
```

**Cascade Rules:**
- **Delete File** → Delete all chunks with matching `file_path` (manual cascade in `SemanticIndex.delete_file_chunks()`)
- **Update File** → Delete old chunks, re-chunk, re-index (incremental rebuild)
- **Delete Language Config** → Chunks remain, but re-chunking falls back to line-based

---

### 4.4 Validation Rules

**CodeChunk Validation:**

| Field | Constraint | Validation |
|-------|-----------|------------|
| `content` | Not empty | `assert len(content) > 0` |
| `file_path` | Valid path | `assert file_path.exists()` |
| `start_line` | Positive | `assert start_line > 0` |
| `end_line` | >= start_line | `assert end_line >= start_line` |
| `chunk_type` | Valid enum | `assert chunk_type in {"function", "class", "import", "module"}` |
| `symbols` | Valid list | `assert isinstance(symbols, list)` |
| `import_ratio` | 0.0-1.0 | `assert 0.0 <= import_ratio <= 1.0` |
| `import_penalty` | 0.0-1.0 | `assert 0.0 <= import_penalty <= 1.0` |
| `token_count` | ≤514 | `assert token_count <= 514` |

**LanguageConfig Validation:**

| Field | Constraint | Validation |
|-------|-----------|------------|
| `language` | Not empty | `assert len(language) > 0` |
| `import_nodes` | Non-empty list | `assert len(import_nodes) > 0` |
| `definition_nodes` | Non-empty list | `assert len(definition_nodes) > 0` |
| `import_penalty` | 0.0-1.0 | `assert 0.0 <= import_penalty <= 1.0` |
| `target_chunk_size` | ≤514 | `assert target_chunk_size <= 514` |

**Runtime Validation:**
- Validation occurs in `__post_init__()` for dataclasses
- Invalid chunks logged and skipped (not indexed)
- Invalid config entries logged and filtered (graceful degradation)
- Validation errors do not block index building (fail-safe)

**Error Examples:**
```python
# Invalid token count
CodeChunk(..., token_count=700)  # AssertionError: token_count exceeds CodeBERT limit

# Invalid import ratio
CodeChunk(..., import_ratio=1.5)  # AssertionError: import_ratio must be 0-1

# Invalid line range
CodeChunk(..., start_line=100, end_line=50)  # AssertionError: Invalid line range
```

---

### 4.5 Data Flow

**Index Build Time:**
```
Source Files → UniversalASTChunker.chunk_file()
    ↓
List[CodeChunk] (validated domain models)
    ↓
SemanticIndex._chunk_file() (converts to dict)
    ↓
CodeBERT.encode() (generates embeddings)
    ↓
LanceDB.add() (stores with vector)
    ↓
code_chunks table (persistent storage)
```

**Query Time:**
```
User Query → SemanticIndex.search()
    ↓
Vector Search (CodeBERT embeddings) → List[{chunk_dict}]
    ↓
FTS Search (keyword matching) → List[{chunk_dict}]
    ↓
RRF Fusion (combine results) → List[{chunk_dict with score}]
    ↓
Apply Import Penalties (score *= import_penalty) → List[{chunk_dict with final_score}]
    ↓
Sort by final_score DESC → Top N results
    ↓
Return to user (with metadata: chunk_type, symbols, etc.)
```

---

**Data Model Summary:**
- **Domain Models**: 2 (CodeChunk, LanguageConfig)
- **Tables**: 1 (code_chunks in LanceDB)
- **Relationships**: 3 (Chunk→File, Chunk→Config, Chunk↔AST)
- **Validation Rules**: 14 total (9 for CodeChunk, 5 for LanguageConfig)

---

## 5. Security Design

This section defines security controls for AST-aware code chunking. Since this is an **internal, local-only feature** with no external APIs or user authentication, security focuses on input validation, resource limits, and safe handling of source code.

---

### 5.1 Threat Model

**Assets:**
- Source code files (potentially containing secrets, proprietary logic)
- Configuration data (mcp.yaml with language settings)
- LanceDB index (embedded vectors, metadata)

**Threats:**
| ID | Threat | Impact | Mitigation |
|----|--------|--------|------------|
| T1 | Malicious file paths (path traversal) | Read files outside workspace | Path validation (NFR-SEC-1) |
| T2 | Malicious AST in crafted code | Parser DOS/crash | Resource limits (NFR-SEC-2) |
| T3 | Secrets in source code indexed | Leak via search | Not mitigated (out of scope) |
| T4 | Malicious mcp.yaml config | Code execution | Config validation (NFR-SEC-3) |
| T5 | Large files DOS index build | System resource exhaustion | File size limits (NFR-SEC-4) |

**Out of Scope:**
- **Secrets management**: Detecting/redacting secrets in source code (separate concern, addressed by tools like `git-secrets`)
- **Access control**: prAxIs OS runs locally with single-user permissions (no RBAC needed)
- **Network security**: No network communication (local-only indexing)

---

### 5.2 Input Validation

**File Path Validation:**
```python
def validate_file_path(file_path: Path, base_path: Path) -> None:
    """Validate file path is within base_path (prevent traversal).
    
    Security:
        - Resolve symlinks to detect escape attempts
        - Check resolved path is child of base_path
        - Reject absolute paths outside workspace
    """
    resolved = file_path.resolve()
    base_resolved = base_path.resolve()
    
    if not str(resolved).startswith(str(base_resolved)):
        raise SecurityError(f"Path traversal detected: {file_path}")
```

**Mitigates:** T1 (Path Traversal)

---

**Configuration Validation:**
```python
def validate_language_config(config: dict) -> LanguageConfig:
    """Validate and sanitize language config from mcp.yaml.
    
    Security:
        - Node types are strings only (no code execution)
        - Import penalty is numeric 0.0-1.0 (no injection)
        - Language name is alphanumeric only
        - No arbitrary Python eval() of config values
    """
    language = config.get("language", "").strip()
    assert re.match(r'^[a-z0-9_]+$', language), "Invalid language name"
    
    import_penalty = float(config.get("import_penalty", 0.3))
    assert 0.0 <= import_penalty <= 1.0, "Invalid import_penalty"
    
    # Node types are strings only (validated by Tree-sitter)
    import_nodes = config.get("import_nodes", [])
    assert all(isinstance(n, str) for n in import_nodes), "Node types must be strings"
    
    return LanguageConfig(language=language, import_penalty=import_penalty, ...)
```

**Mitigates:** T4 (Malicious Config)

---

**Token Limit Enforcement:**
```python
def chunk_file(self, file_path: Path) -> List[CodeChunk]:
    """Chunk file with token limit enforcement.
    
    Security:
        - Enforce 514 token hard limit (CodeBERT)
        - Split oversized chunks at boundaries
        - Fail-safe: Skip chunk if split fails
    """
    chunks = self._extract_chunks(file_path)
    
    for chunk in chunks:
        if chunk.token_count > 514:
            # Attempt to split at boundaries
            split_chunks = self._split_large_chunk(chunk)
            if any(c.token_count > 514 for c in split_chunks):
                logger.warning(f"Unable to split chunk in {file_path}, skipping")
                continue  # Skip unsplittable chunk (fail-safe)
```

**Mitigates:** T2 (Parser DOS via large chunks)

---

### 5.3 Resource Limits

**File Size Limits:**
```python
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def should_index_file(file_path: Path) -> bool:
    """Check if file should be indexed (size limit).
    
    Security:
        - Reject files >10MB (prevent index bloat)
        - Log rejected files for transparency
    """
    if file_path.stat().st_size > MAX_FILE_SIZE:
        logger.warning(f"File too large, skipping: {file_path} ({file_path.stat().st_size} bytes)")
        return False
    return True
```

**Mitigates:** T5 (Large file DOS)

---

**Parse Timeout:**
```python
PARSE_TIMEOUT = 30  # seconds

def parse_with_timeout(parser, code: str, timeout: int = PARSE_TIMEOUT) -> Optional[Tree]:
    """Parse code with timeout (prevent infinite loops).
    
    Security:
        - Timeout prevents malicious code from hanging parser
        - Returns None on timeout (graceful fallback)
    """
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Parse timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        tree = parser.parse(bytes(code, "utf8"))
        signal.alarm(0)  # Cancel alarm
        return tree
    except TimeoutError:
        logger.warning(f"Parse timeout, falling back to line-based chunking")
        return None
```

**Mitigates:** T2 (Parser DOS)

---

### 5.4 Data Protection

**Source Code Handling:**
- **Storage**: Source code indexed as plaintext in LanceDB (no encryption at rest)
  - **Rationale**: Index is local-only, same security boundary as source files
  - **Alternative**: Encrypt LanceDB index with disk-level encryption (e.g., FileVault, LUKS)
- **Logging**: File paths logged (no code content in logs)
- **Secrets**: No automatic secret detection (use external tools like `git-secrets`, `trufflehog`)

**Configuration Security:**
- **mcp.yaml**: Read-only at runtime (loaded once at server start)
- **Validation**: Strict schema validation, no dynamic code execution
- **Defaults**: Safe fallback values for all config fields

---

### 5.5 Tree-sitter Security

**Parser Safety:**
Tree-sitter is designed to safely parse untrusted code:
- **No code execution**: Parser only generates AST (no eval/exec)
- **Memory-safe**: Written in C with Rust bindings (no buffer overflows)
- **Error recovery**: Gracefully handles syntax errors (no crashes)
- **Tested**: Tree-sitter parsers fuzz-tested by maintainers

**Risks:**
- **Parser bugs**: Rare but possible (e.g., infinite loop on malformed input)
- **Mitigation**: Timeout enforcement, fallback to line-based chunking

**References:**
- Tree-sitter security: https://tree-sitter.github.io/tree-sitter/#security
- Parser fuzzing: https://github.com/tree-sitter/tree-sitter/tree/master/fuzz

---

### 5.6 Operational Security

**Index Integrity:**
- **No remote access**: LanceDB index stored locally in `.praxis-os/.cache/indexes/code`
- **Backup**: Index is rebuildable from source (no backup needed for security)
- **Corruption detection**: Health checks detect index corruption, trigger rebuild

**Rollback Security:**
- **Backup validation**: SHA256 checksums for rollback archives
- **Atomic operations**: Config rollback uses atomic file writes
- **Audit trail**: Rollback events logged with timestamp and reason

**Dependency Security:**
- **Tree-sitter**: Mature, widely-used library (used by GitHub, Atom, Neovim)
- **CodeBERT**: Pre-trained model from Microsoft (no user data sent to cloud)
- **LanceDB**: Open-source, local-only (no network calls)

---

### 5.7 Security Checklist

| Control | Status | NFR | Evidence |
|---------|--------|-----|----------|
| Path validation (traversal) | ✅ | NFR-SEC-1 | `validate_file_path()` |
| File size limits (10MB) | ✅ | NFR-SEC-4 | `should_index_file()` |
| Parse timeout (30s) | ✅ | NFR-SEC-2 | `parse_with_timeout()` |
| Config validation | ✅ | NFR-SEC-3 | `validate_language_config()` |
| Token limit enforcement (514) | ✅ | NFR-SEC-2 | `chunk_file()` validation |
| No code execution in config | ✅ | NFR-SEC-3 | String-only node types |
| Secrets detection | ❌ | Out of scope | Use external tools |
| Encryption at rest | ❌ | Not required | Same boundary as source |
| Access control | ❌ | Not required | Local single-user only |

---

### 5.8 Security Requirements Traceability

| SRD Requirement | Security Control | Implementation |
|----------------|------------------|----------------|
| (No explicit security requirements in SRD) | Path validation | `validate_file_path()` |
| NFR-R1 (Graceful degradation) | Parse timeout, fallback | `parse_with_timeout()` |
| NFR-M1 (Config-driven) | Config validation | `validate_language_config()` |
| NFR-P2 (Index build time <10 min) | File size limits | `should_index_file()` |

**Note**: No explicit security requirements were defined in srd.md because this is an internal, local-only feature with no user-facing attack surface. Security controls focus on defensive programming (input validation, resource limits) rather than authentication/authorization.

---

**Security Summary:**
- **Threats Identified**: 5 (T1-T5)
- **Controls Implemented**: 5 (path validation, config validation, file size limits, parse timeout, token enforcement)
- **Out of Scope**: 3 (secrets detection, encryption at rest, access control)
- **Security Model**: Defense in depth (validation + limits + fallback)

---

## 6. Performance Design

This section defines performance strategies, optimizations, and monitoring to meet non-functional requirements (NFR-P1, NFR-P2, NFR-P3).

---

### 6.1 Performance Targets

**Search Query Performance (NFR-P1):**

| Metric | Baseline (Line-Based) | Target (AST-Aware) | Status |
|--------|----------------------|-------------------|--------|
| p50 latency | <100ms | <100ms | Must maintain |
| p95 latency | <200ms | <200ms | Must maintain |
| p99 latency | <300ms | <300ms | Must maintain |
| Import penalty overhead | N/A | <1ms | New |

**Rationale:** AST chunking happens at index build time, not query time. Search latency should not regress.

---

**Index Build Performance (NFR-P2):**

| Metric | Baseline (Line-Based) | Target (AST-Aware) | Acceptable Overhead |
|--------|----------------------|-------------------|---------------------|
| 100K LOC | <5 minutes | <10 minutes | 2-3x slower |
| Throughput | 1000 files/sec | 300-500 files/sec | One-time cost |
| Incremental rebuild | <30 seconds | <60 seconds | For changed files only |

**Rationale:** AST parsing is computationally expensive (2-3x slower than line splitting), but this is a one-time cost at index build time.

---

**Import Penalty Application (NFR-P3):**

| Metric | Target | Measurement |
|--------|--------|-------------|
| Penalty calculation | <0.5ms per chunk | Profiled in RRF fusion |
| Penalty application | <0.5ms total | O(n) where n=result count |
| Total overhead | <1ms | End-to-end |

**Rationale:** Import penalty is a simple multiplication (`score *= penalty`), negligible overhead.

---

### 6.2 Caching Strategy

**L1: Tree-sitter Parser Cache**
```python
class UniversalASTChunker:
    _parser_cache: Dict[str, Parser] = {}  # Class-level cache
    _cache_lock: threading.Lock = threading.Lock()
    
    def __init__(self, language: str, config: dict, base_path: Path):
        # Reuse cached parser (avoid repeated grammar loading)
        with self._cache_lock:
            if language not in self._parser_cache:
                self._parser_cache[language] = self._load_parser(language)
            self._parser = self._parser_cache[language]
```

**Benefits:**
- Avoid repeated grammar loading (5-10ms per file → 0ms after first load)
- Shared across all chunker instances for same language
- Thread-safe with lock

---

**L2: Gitignore Parser Cache**
```python
_gitignore_cache: Dict[Path, IgnoreParser] = {}  # Cache by .gitignore path

def _get_gitignore_parser(self, gitignore_path: Path) -> IgnoreParser:
    if gitignore_path not in self._gitignore_cache:
        self._gitignore_cache[gitignore_path] = IgnoreParser(gitignore_path)
    return self._gitignore_cache[gitignore_path]
```

**Benefits:**
- Avoid repeated `.gitignore` parsing (10-20ms → 0ms)
- Cache invalidation on file change (check mtime)

---

**L3: Language Config Cache**
```python
class ASTExtractor:
    def __init__(self, languages: List[str], base_path: Path, config: dict):
        # Load all language configs once at initialization
        self.lang_configs = {
            lang: config["language_configs"].get(lang, {})
            for lang in languages
        }
```

**Benefits:**
- Config loaded once at server startup (not per file)
- Immutable at runtime (no cache invalidation needed)

---

### 6.3 Index Build Optimization

**Parallel Processing:**
```python
from concurrent.futures import ThreadPoolExecutor

def build(self, source_paths: List[Path], force: bool = False) -> None:
    """Build index with parallel chunking."""
    files = self._collect_files(source_paths)
    
    # Chunk files in parallel (CPU-bound)
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        chunk_futures = {
            executor.submit(self._chunk_file, file): file
            for file in files
        }
        
        # Collect chunks as they complete
        all_chunks = []
        for future in as_completed(chunk_futures):
            chunks = future.result()
            all_chunks.extend(chunks)
    
    # Batch embed (GPU-friendly)
    embeddings = self._batch_embed([c.content for c in all_chunks])
    
    # Batch insert (I/O efficient)
    self._table.add(all_chunks, vectors=embeddings)
```

**Optimizations:**
- **Parallel chunking**: Utilize all CPU cores (8 cores → 8x faster)
- **Batch embedding**: Send multiple chunks to CodeBERT at once (reduce overhead)
- **Batch insert**: Single LanceDB transaction (avoid per-chunk writes)

**Expected Speedup:**
- Single-threaded: 10 minutes for 100K LOC
- Multi-threaded (8 cores): ~2 minutes for 100K LOC

---

**Incremental Rebuild:**
```python
def rebuild_file(self, file_path: Path) -> None:
    """Incrementally rebuild index for single file."""
    # Delete old chunks for this file
    self._table.delete(f"file_path = '{file_path}'")
    
    # Re-chunk file
    chunks = self._chunk_file(file_path)
    
    # Re-embed and insert
    embeddings = self._batch_embed([c.content for c in chunks])
    self._table.add(chunks, vectors=embeddings)
```

**Use Case:** File watcher detects changes, triggers incremental rebuild for changed files only.

---

### 6.4 Query Optimization

**Import Penalty Application:**
```python
def search(self, query: str, n_results: int = 5) -> List[Dict]:
    """Execute hybrid search with import penalties."""
    # 1. Vector search (LanceDB HNSW, ~50ms)
    vector_results = self._vector_search(query, n_results * 2)
    
    # 2. FTS search (LanceDB FTS, ~30ms)
    fts_results = self._fts_search(query, n_results * 2)
    
    # 3. RRF fusion (in-memory, ~5ms)
    fused_results = self._rrf_fusion(vector_results, fts_results)
    
    # 4. Apply import penalties (in-memory, <1ms)
    for result in fused_results:
        if result["chunk_type"] == "import" and result["import_ratio"] > 0.5:
            result["score"] *= result["import_penalty"]  # 0.3 default
    
    # 5. Re-sort and return top N
    fused_results.sort(key=lambda r: r["score"], reverse=True)
    return fused_results[:n_results]
```

**Performance Breakdown:**
- Vector search: 50ms (HNSW approximate)
- FTS search: 30ms (inverted index)
- RRF fusion: 5ms (O(n log n) sort)
- Import penalty: <1ms (O(n) multiplication)
- **Total: ~86ms p50, <200ms p95**

---

**HNSW Index Tuning:**
```yaml
vector:
  model: "microsoft/codebert-base"
  dimension: 768
  index_config:
    type: "HNSW"
    M: 32                  # Neighbors per node (default 16)
    ef_construction: 200   # Build-time search breadth (default 100)
    ef_search: 100         # Query-time search breadth (default 50)
```

**Trade-offs:**
- Higher M: Better recall, larger index size (+50% disk)
- Higher ef_search: Better recall, slower queries (+20ms)
- **Chosen config**: Balance recall (>95%) and latency (<200ms p95)

---

### 6.5 Monitoring & Observability

**Key Performance Indicators (KPIs):**

| KPI | Metric | Target | Alert Threshold |
|-----|--------|--------|----------------|
| Search Latency | p95 response time | <200ms | >300ms (warning) |
| Index Build Time | 100K LOC rebuild | <10 min | >15 min (warning) |
| Import Penalty Overhead | Per-query overhead | <1ms | >5ms (warning) |
| Fallback Rate | % files using line-based | <25% | >50% (degraded) |
| AST Parse Success Rate | % files parsed successfully | >75% | <50% (failure) |

---

**Metrics Collection:**
```python
from prometheus_client import Histogram, Counter, Gauge

# Search latency histogram
search_latency = Histogram(
    'code_search_latency_seconds',
    'Code search query latency',
    buckets=[0.05, 0.1, 0.2, 0.3, 0.5, 1.0]
)

# Index build time gauge
index_build_time = Gauge(
    'code_index_build_seconds',
    'Code index build time'
)

# Fallback counter
fallback_count = Counter(
    'code_chunking_fallback_total',
    'AST chunking fallback activations',
    ['language', 'reason']
)

# Import penalty applications
import_penalty_applied = Counter(
    'code_search_import_penalty_total',
    'Import penalty applications'
)
```

---

**Health Check Integration:**
```python
def health_check(self) -> HealthStatus:
    """Report AST chunker health with performance metrics."""
    return HealthStatus(
        healthy=self.fallback_rate < 0.25,
        message=f"AST chunker {'operational' if self.fallback_rate < 0.25 else 'degraded'}",
        details={
            "chunk_count": self.total_chunks,
            "fallback_count": self.fallback_count,
            "fallback_rate": self.fallback_rate,
            "avg_token_size": self.avg_token_size,
            "avg_import_ratio": self.avg_import_ratio,
            "parse_success_rate": self.parse_success_rate,
            "performance": {
                "last_build_time_seconds": self.last_build_time,
                "avg_search_latency_p95_ms": self.avg_search_latency_p95,
                "import_penalty_overhead_ms": self.import_penalty_overhead
            }
        }
    )
```

---

**Performance Testing Strategy:**

**Unit Performance Tests:**
```python
def test_chunk_file_performance():
    """Verify chunking performance meets target."""
    chunker = UniversalASTChunker("python", config, base_path)
    file_path = Path("large_file.py")  # 1000 LOC
    
    start = time.time()
    chunks = chunker.chunk_file(file_path)
    duration = time.time() - start
    
    assert duration < 0.5, f"Chunking too slow: {duration}s"
    assert len(chunks) > 0, "No chunks generated"
```

**Integration Performance Tests:**
```python
def test_search_latency_p95():
    """Verify search latency meets NFR-P1."""
    index = SemanticIndex(config)
    
    # Execute 100 queries
    latencies = []
    for query in test_queries:
        start = time.time()
        results = index.search(query, n_results=5)
        latencies.append(time.time() - start)
    
    p95 = np.percentile(latencies, 95)
    assert p95 < 0.2, f"p95 latency too high: {p95}s"
```

**Load Testing:**
```bash
# Simulate concurrent searches
locust -f tests/load/search_load.py --users 100 --spawn-rate 10
```

---

### 6.6 Scalability Considerations

**Current Scale:**
- **100K LOC**: Target deployment (prAxIs OS codebase)
- **Index size**: ~500MB (vectors + FTS)
- **Rebuild time**: <10 minutes (8-core CPU)
- **Query latency**: <200ms p95

**Future Scale (10x):**
- **1M LOC**: Large enterprise monorepo
- **Index size**: ~5GB (still manageable on disk)
- **Rebuild time**: ~60 minutes (acceptable for overnight/CI)
- **Query latency**: <200ms p95 (HNSW scales logarithmically)

**Scaling Limits:**
- **LanceDB**: Handles multi-GB indexes efficiently (columnar format)
- **HNSW**: O(log n) query time (minimal impact from 10x scale)
- **CodeBERT**: Batch size limited by GPU memory (process in batches)

**Scale-Out Strategy (if needed):**
1. **Partition by language**: Separate indexes for Python, TypeScript, Go
2. **Partition by module**: Separate indexes for `ouroboros/`, `tests/`, etc.
3. **Distributed LanceDB**: Future feature (not available yet)

---

### 6.7 Performance Regression Prevention

**CI/CD Performance Tests:**
```yaml
# .github/workflows/performance.yml
- name: Performance regression test
  run: |
    pytest tests/performance/ --benchmark-only
    # Fail if p95 latency > 200ms
    python scripts/check_performance_regression.py
```

**Benchmarking:**
- Store baseline performance metrics in repo
- Compare each PR against baseline
- Block merge if regression >10%

---

**Performance Summary:**
- **Search latency**: <200ms p95 (no regression from baseline)
- **Index build time**: <10 minutes for 100K LOC (2-3x slower, acceptable)
- **Import penalty overhead**: <1ms (negligible)
- **Monitoring**: 5 KPIs, Prometheus metrics, health check integration
- **Scalability**: Handles 1M LOC with <200ms p95

---

