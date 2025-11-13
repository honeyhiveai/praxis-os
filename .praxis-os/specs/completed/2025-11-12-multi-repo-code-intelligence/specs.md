# Technical Specifications

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Based on:** srd.md (requirements)

---

## 1. Architecture Overview

### 1.1 Architectural Pattern

**Primary Pattern:** Partition-Based Modular Monolith with Dynamic Discovery

**Rationale:**
- **Single Process:** All code intelligence functionality runs in one Python process (MCP server), simplifying deployment and debugging
- **Logical Partitioning:** Repositories grouped into partitions (primary, instrumentors) for operational isolation without service boundaries
- **Dynamic Discovery:** Partitions auto-discovered from configuration at runtime, enabling addition/removal without code changes
- **Shared Infrastructure:** All partitions share Tree-sitter, LanceDB, DuckDB engines for efficiency

**Key Characteristics:**
- Modular design with clear boundaries (CodeIndex → CodePartition → Sub-Indexes)
- Single codebase, single deployment artifact
- Config-driven behavior (zero hardcoded partition names)
- Fractal health check architecture (4-level hierarchy)

---

### 1.2 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          prAxIs OS MCP Server                                │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          IndexManager                                 │   │
│  │  ┌─────────────────┐  ┌───────────────────────────────────────────┐│   │
│  │  │ StandardsIndex  │  │          CodeIndex                        ││   │
│  │  │ (markdown docs) │  │  (Multi-Repo, Partition-Based)            ││   │
│  │  └─────────────────┘  │                                           ││   │
│  │                        │  ┌─────────────────┬─────────────────┐  ││   │
│  │                        │  │  Partition:     │  Partition:     │  ││   │
│  │                        │  │  PRIMARY        │  INSTRUMENTORS  │  ││   │
│  │                        │  ├─────────────────┼─────────────────┤  ││   │
│  │                        │  │ Repos:          │ Repos:          │  ││   │
│  │                        │  │ • praxis-os     │ • openlit/...   │  ││   │
│  │                        │  │ • python-sdk    │ • traceloop/... │  ││   │
│  │                        │  │ • hive-kube     │ • arize/...     │  ││   │
│  │                        │  │                 │ • otel/...      │  ││   │
│  │                        │  │ 113K chunks     │ 324K chunks     │  ││   │
│  │                        │  │ p95 < 50ms      │ p95 < 200ms     │  ││   │
│  │                        │  │                 │                 │  ││   │
│  │                        │  │ ┌─────────────┐ │ ┌─────────────┐│  ││   │
│  │                        │  │ │ Semantic    │ │ │ Semantic    ││  ││   │
│  │                        │  │ │ Index       │ │ │ Index       ││  ││   │
│  │                        │  │ │ (LanceDB)   │ │ │ (LanceDB)   ││  ││   │
│  │                        │  │ └─────────────┘ │ └─────────────┘│  ││   │
│  │                        │  │ ┌─────────────┐ │ ┌─────────────┐│  ││   │
│  │                        │  │ │ AST Index   │ │ │ AST Index   ││  ││   │
│  │                        │  │ │ (DuckDB)    │ │ │ (DuckDB)    ││  ││   │
│  │                        │  │ └─────────────┘ │ └─────────────┘│  ││   │
│  │                        │  │ ┌─────────────┐ │ ┌─────────────┐│  ││   │
│  │                        │  │ │ Graph Index │ │ │ Graph Index ││  ││   │
│  │                        │  │ │ (DuckDB)    │ │ │ (DuckDB)    ││  ││   │
│  │                        │  │ │ cross-repo  │ │ │ per-repo    ││  ││   │
│  │                        │  │ └─────────────┘ │ └─────────────┘│  ││   │
│  │                        │  └─────────────────┴─────────────────┘  ││   │
│  │                        └───────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Supporting Components                              │   │
│  │  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐       │   │
│  │  │ Repository    │  │ Repository     │  │ Incremental      │       │   │
│  │  │ Tracker       │  │ Syncer         │  │ Indexer          │       │   │
│  │  │ (DuckDB)      │  │ (Git Ops)      │  │ (Changed Files)  │       │   │
│  │  └───────────────┘  └────────────────┘  └──────────────────┘       │   │
│  │                                                                       │   │
│  │  ┌───────────────┐  ┌────────────────┐  ┌──────────────────┐       │   │
│  │  │ Tree-sitter   │  │ AST-Aware      │  │ Cascading Health │       │   │
│  │  │ Parser Engine │  │ Chunker        │  │ Check System     │       │   │
│  │  └───────────────┘  └────────────────┘  └──────────────────┘       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   Client-Facing Tools                                │   │
│  │  ┌───────────────────────────────────┐  ┌──────────────────────┐   │   │
│  │  │ pos_search_project                │  │ Extraction Workflows │   │   │
│  │  │ • search_code (Semantic)          │  │ • extract_attributes │   │   │
│  │  │ • search_ast (Structural)         │  │ • extract_span_naming│   │   │
│  │  │ • find_callers/dependencies       │  │ • extract_events     │   │   │
│  │  │ • Partition/repo/provider filters │  │ • output_yaml/json   │   │   │
│  │  └───────────────────────────────────┘  └──────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                ┌───────────────────────────────────────┐
                │   Configuration (mcp.yaml)            │
                │   • Partition definitions             │
                │   • Repository URLs/paths             │
                │   • Performance targets               │
                │   • Cross-repo graph flags            │
                └───────────────────────────────────────┘
```

---

### 1.3 Architectural Decisions

#### Decision 1: Partition-Based Scaling (vs. Single Unified Index)

**Decision:** Group repositories into logical partitions (primary, instrumentors) with independent indexes.

**Rationale:**
- **Addresses FR-002:** Partition-Based Index Organization requirement
- **Addresses NFR-P1/P2:** Different performance targets for primary (p95 < 50ms) vs instrumentors (p95 < 200ms)
- **Operational Isolation:** Primary codebase queries remain fast even with 270 instrumentors indexed
- **Targeted Rebuilds:** Rebuild only affected partition when repos change
- **Clear Boundaries:** Separates "your code" (primary) from "analysis targets" (instrumentors)

**Alternatives Considered:**
- **Single Unified Index:** Simpler but mixes fast/slow queries, hard to meet different p95 targets
- **Microservices per Partition:** Over-engineering for single-developer use case, deployment complexity

**Trade-offs:**
- **Pros:** Performance isolation, operational clarity, scalable to 437K chunks
- **Cons:** Slightly more complex config, potential data duplication if repos appear in multiple partitions (prevented via validation)

---

#### Decision 2: Dynamic Config-Driven Discovery (vs. Hardcoded Partitions)

**Decision:** Partitions auto-discovered from `mcp.yaml` at runtime, zero hardcoded partition names in code.

**Rationale:**
- **Addresses FR-010:** Partition Lifecycle Management (CRUD) requirement
- **Addresses NFR-M4:** Configuration-Driven Architecture (zero hardcoded paths)
- **Extensibility:** Add new partitions (e.g., "monorepos", "dependencies") without code changes
- **Future-Proof:** Supports nested partitions for > 500K chunks (per-provider subpartitions)

**Alternatives Considered:**
- **Hardcoded Partitions:** Faster initial implementation but requires code changes for new partitions
- **Database-Driven Config:** More complex, no clear benefit over YAML for this use case

**Trade-offs:**
- **Pros:** Maximum flexibility, supports evolving use cases, config changes don't require code deployment
- **Cons:** Config validation required, potential for user error in YAML syntax

---

#### Decision 3: Parse-Once-Index-Thrice (vs. Independent Indexing)

**Decision:** Single Tree-sitter parse per file populates all 3 indexes (Semantic, AST, Graph) in one pass.

**Rationale:**
- **Addresses NFR-P4:** Incremental Update Performance (< 5 seconds for typical changes)
- **Efficiency:** Tree-sitter parsing is the bottleneck; parsing once and extracting 3 data structures is 3x faster than parsing 3 times
- **Atomic Updates:** All 3 indexes updated together prevents inconsistency
- **Addresses NFR-R4:** Atomic Updates requirement

**Alternatives Considered:**
- **Independent Indexing:** Each index parses files separately, 3x slower, potential inconsistency

**Trade-offs:**
- **Pros:** 3x faster indexing, guaranteed consistency across indexes
- **Cons:** Slightly more complex indexer logic (one pipeline with 3 outputs)

---

#### Decision 4: Soft Delete with Archival (vs. Hard Delete)

**Decision:** Partition deletion archives index data to `.archive/{partition}_{timestamp}/` instead of immediate deletion.

**Rationale:**
- **Addresses NFR-R3:** Rollback Capability requirement
- **Addresses NFR-O2:** Partition Lifecycle Observability (audit trail)
- **Risk Mitigation:** Accidental partition deletion recoverable
- **Testing/Debugging:** Can compare before/after states

**Alternatives Considered:**
- **Hard Delete:** Irreversible, no recovery, faster cleanup but higher risk
- **Database Transactions:** DuckDB/LanceDB don't support cross-file ACID, soft delete is safer

**Trade-offs:**
- **Pros:** Rollback capability (< 2 min), audit trail, safe deletion
- **Cons:** Requires disk space (< 10% of active index per NFR-ST3), manual cleanup of old archives

---

#### Decision 5: Cross-Repo Call Graphs (Configurable per Partition)

**Decision:** Enable/disable cross-repo graph edges via `graph_cross_repo` flag in partition config.

**Rationale:**
- **Addresses FR-006:** Configurable Cross-Repository Call Graphs requirement
- **Use Case Driven:** Primary partition needs cross-project call graphs (praxis-os ↔ python-sdk), instrumentors don't (each instrumentor isolated)
- **Performance:** Isolated graphs reduce query complexity for instrumentors partition

**Alternatives Considered:**
- **Always Enable:** Simpler but creates unnecessary edges in instrumentors, slower queries
- **Always Disable:** Simpler but breaks primary partition use case (multi-project analysis)

**Trade-offs:**
- **Pros:** Flexibility for different use cases, optimal performance per partition
- **Cons:** Config complexity, requires `caller_repo`/`callee_repo` tracking in GraphIndex

---

### 1.4 Requirements Traceability

| Requirement | Architectural Element | How Addressed |
|-------------|----------------------|---------------|
| FR-001: Multi-Repo Indexing | CodePartition with multiple RepositoryConfig | Each partition contains list of repositories, tracked via RepositoryTracker |
| FR-002: Partition Organization | CodeIndex → CodePartition hierarchy | Dynamic discovery from config, independent indexes per partition |
| FR-003: Repository State Tracking | RepositoryTracker (DuckDB `repository_state` table) | Tracks commit hash, indexed time, file count, status per repo |
| FR-004: Incremental Updates | IncrementalIndexer + RepositoryTracker | Git diff to detect changes, update only changed files across all 3 indexes |
| FR-005: Cross-Repo Filtering | Enhanced metadata in all indexes | partition/repo_name/provider columns in Semantic, AST, Graph indexes |
| FR-006: Configurable Call Graphs | `graph_cross_repo` flag in partition config | Enables/disables cross-repo edges via caller_repo/callee_repo filtering |
| FR-007: Git Synchronization | RepositorySyncer component | Clone, pull, sparse checkout via standard Git operations |
| FR-008: Extraction Workflows | Extraction workflow layer above pos_search_project | Query templates for attributes, span naming, events |
| FR-009: Machine-Readable Output | Output generator component | YAML/JSON export with structured schema |
| FR-010: Partition Lifecycle | PartitionManager + startup validation | CRUD operations, soft delete, orphaned data detection, config validation |
| NFR-P1/P2: Query Latency | Per-partition indexes with different targets | Primary: p95 < 50ms, Instrumentors: p95 < 200ms (measured via `performance_targets` in config) |
| NFR-ST1/ST2/ST3: Storage | Incremental indexing + sparse checkout + soft delete archival | Total < 3GB, incremental storage, archives < 10% of active index |
| NFR-M1/M2/M3/M4: Maintainability | Parameterized query templates, version-controlled workflows, config-driven | Query templates reusable, extraction scripts in Git, zero hardcoding |
| NFR-R1/R2/R3/R4: Reliability | Graceful error handling, per-repo health checks, soft delete, atomic updates | Parse errors skip file, health check per repo, rollback via archive, parse-once-index-thrice |
| NFR-SC1/SC2/SC3: Scalability | Single-table architecture with partitioning, dynamic config, concurrent queries | 437K chunks supported, add providers via config, concurrent query design |
| NFR-O1/O2/O3/O4: Operability | Startup validation, audit logs, Cascading Health Check integration, config validation | Validate on startup, log all CRUD, fractal 4-level health checks, reject invalid config |

---

### 1.5 Technology Stack

**Runtime Environment:**
- **Language:** Python 3.11+
- **Process Model:** Single Python process (MCP server)

**Indexes:**
- **Semantic Search:** LanceDB (vector embeddings + full-text search + RRF)
  - Embedding Model: CodeBERT (6 languages: Python, Java, JavaScript, Go, PHP, Ruby)
- **AST Search:** DuckDB (SQL queries on `ast_nodes` table)
  - Parser: Tree-sitter (18+ languages)
- **Graph Traversal:** DuckDB (recursive CTEs on `symbols` and `relationships` tables)

**Data Storage:**
- **LanceDB:** Semantic index chunks (`.lance` format, columnar)
- **DuckDB:** AST nodes, graph symbols/relationships, repository state (`.duckdb` files)
- **Git:** Repository clones (local or network)

**Configuration:**
- **mcp.yaml:** Main config file (YAML)
- **Pydantic:** Config validation and schemas

**Supporting Libraries:**
- **Tree-sitter:** AST parsing
- **GitPython:** Git operations (clone, pull, diff)
- **PyYAML:** Config parsing
- **Pydantic:** Config validation

**Integration:**
- **MCP (Model Context Protocol):** Client-server communication
- **pos_search_project Tool:** Unified search API exposed to AI agents

**Observability:**
- **Cascading Health Check System:** Fractal 4-level health checks (CodeIndex → Partition → Index Type → Sub-components)
- **Logs:** Structured logging to `mcp.log`
- **Metrics:** Query latency (p95), chunk counts, repo counts per partition

**Development/Testing:**
- **pytest:** Unit and integration tests
- **mypy:** Type checking
- **ruff:** Linting

---

### 1.6 Deployment Architecture

**Deployment Model:** Local Development Tool (Single-Machine)

```
┌─────────────────────────────────────────────────────────────┐
│  User's Development Machine                                  │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Cursor IDE / Terminal                              │   │
│  │  (AI Agent Workspace)                               │   │
│  └────────────────┬────────────────────────────────────┘   │
│                   │ MCP Protocol                             │
│                   ▼                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  prAxIs OS MCP Server                               │   │
│  │  • Python Process                                   │   │
│  │  • IndexManager (Standards + Code)                  │   │
│  │  • Cascading Health Checks                          │   │
│  │  • pos_search_project Tool                          │   │
│  └────────────────┬────────────────────────────────────┘   │
│                   │ File I/O                                 │
│                   ▼                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Local Filesystem                                   │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ /Users/josh/.praxis-os/indexes/                │ │   │
│  │  │ ├─ code/                                       │ │   │
│  │  │ │  ├─ primary/ (113K chunks, ~500MB)          │ │   │
│  │  │ │  │  ├─ semantic.lance (LanceDB)             │ │   │
│  │  │ │  │  ├─ ast.duckdb (DuckDB)                  │ │   │
│  │  │ │  │  └─ graph.duckdb (DuckDB)                │ │   │
│  │  │ │  ├─ instrumentors/ (324K chunks, ~2GB)      │ │   │
│  │  │ │  │  ├─ semantic.lance                        │ │   │
│  │  │ │  │  ├─ ast.duckdb                            │ │   │
│  │  │ │  │  └─ graph.duckdb                          │ │   │
│  │  │ │  └─ .archive/ (soft delete backups)         │ │   │
│  │  │ ├─ standards/ (markdown docs, ~50MB)           │ │   │
│  │  │ └─ repository_state.duckdb (tracker)           │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  │                                                     │   │
│  │  ┌───────────────────────────────────────────────┐ │   │
│  │  │ /Users/josh/src/github.com/                    │ │   │
│  │  │ ├─ praxis-os/ouroboros/ (primary partition)   │ │   │
│  │  │ ├─ python-sdk/src/ (primary partition)        │ │   │
│  │  │ └─ vendor/ (instrumentors partition)           │ │   │
│  │  │    ├─ openlit/sdk/python/src/openlit/...      │ │   │
│  │  │    ├─ traceloop/packages/...                   │ │   │
│  │  │    └─ arize/python/instrumentation/...         │ │   │
│  │  └───────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Deployment Steps:**
1. **Install prAxIs OS:** `pip install -e .` (editable install)
2. **Configure Partitions:** Edit `config/mcp.yaml` with partition/repository definitions
3. **Start MCP Server:** Automatic startup when Cursor launches with MCP enabled
4. **Initial Index Build:** Server auto-builds indexes on first startup (cold start: ~10 minutes for 270 instrumentors)
5. **Incremental Updates:** Triggered manually or via cron for repository sync

**Resource Requirements:**
- **CPU:** 4+ cores recommended for parallel indexing
- **RAM:** 8GB recommended (3.5GB typical usage per NFR)
- **Disk:** 3GB for indexes + repository clones (varies by sparse checkout config)
- **Network:** Required for initial Git clones of remote repositories

**Scaling Considerations:**
- **Current Scale:** 437K chunks (87% of 500K single-table threshold)
- **Future Scale:** Nested partitioning for > 500K chunks (per-provider subpartitions)
- **Performance:** Partition routing ensures fast queries (primary p95 < 50ms, even with 437K total chunks)

---

## 2. Component Design

### 2.1 Component: CodeIndex

**Purpose:** Top-level container managing multiple partitions dynamically discovered from configuration.

**Responsibilities:**
- Discover and instantiate partitions from `mcp.yaml` at runtime
- Route search queries to appropriate partition based on filters
- Aggregate health check results across all partitions
- Provide unified API for all code intelligence operations

**Requirements Satisfied:**
- FR-002: Partition-Based Index Organization (dynamic discovery)
- NFR-M4: Configuration-Driven Architecture (zero hardcoding)
- NFR-O3: Cascading Health Check Integration (fractal hierarchy)

**Public Interface:**
```python
class CodeIndex(BaseIndex):
    def __init__(self, config: CodeIndexConfig, base_path: Path):
        """Initialize CodeIndex with dynamic partition discovery."""
        self.partitions: Dict[str, CodePartition] = {}
        # Dynamically discover partitions from config
        for partition_name, partition_config in config.partitions.items():
            self.partitions[partition_name] = CodePartition(
                name=partition_name,
                config=partition_config,
                base_path=base_path / partition_name
            )
    
    def search(self, query: str, action: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Route search to appropriate partition(s)."""
        pass
    
    def health_check(self) -> HealthStatus:
        """Aggregate health status from all partitions."""
        pass
    
    def get_partition(self, name: str) -> CodePartition:
        """Retrieve specific partition by name."""
        pass
```

**Dependencies:**
- Requires: `CodeIndexConfig` (Pydantic model from `mcp.yaml`)
- Provides: Unified search API, health check aggregation
- Uses: `CodePartition` instances

**Error Handling:**
- Invalid partition name → Raise ValueError with available partitions
- Empty partitions dict → Log warning, continue with empty index
- Partition initialization failure → Log error, skip partition, report in health check

---

### 2.2 Component: CodePartition

**Purpose:** Logical grouping of repositories with independent Semantic, AST, and Graph indexes.

**Responsibilities:**
- Manage 3 sub-indexes (Semantic, AST, Graph) with unified lifecycle
- Track repositories assigned to partition
- Implement partition-specific health checks
- Support incremental rebuilds for changed repositories
- Provide partition-level search filtering

**Requirements Satisfied:**
- FR-001: Multi-Repository Indexing (groups multiple repos)
- FR-002: Partition-Based Index Organization (operational isolation)
- FR-006: Configurable Cross-Repository Call Graphs (per-partition flag)
- NFR-P1/P2: Query Latency (different targets per partition)

**Public Interface:**
```python
class CodePartition:
    def __init__(self, name: str, config: PartitionConfig, base_path: Path):
        """Initialize partition with 3 sub-indexes."""
        self.name = name
        self.config = config
        self.semantic = SemanticIndex(base_path / "semantic.lance", config)
        self.ast = ASTIndex(base_path / "ast.duckdb", config)
        self.graph = GraphIndex(base_path / "graph.duckdb", config)
        self.repositories: List[str] = [repo.name for repo in config.repositories]
    
    def search(self, query: str, action: str, **kwargs) -> List[Dict]:
        """Route to appropriate sub-index (Semantic/AST/Graph)."""
        pass
    
    def health_check(self) -> HealthStatus:
        """Fractal health check for all 3 sub-indexes."""
        pass
    
    def rebuild_incremental(self, repo_name: Optional[str] = None):
        """Rebuild changed files for specific repo or all repos in partition."""
        pass
    
    def add_repository(self, repo_config: RepositoryConfig):
        """Add new repository to partition (incremental index)."""
        pass
    
    def remove_repository(self, repo_name: str):
        """Remove repository from partition (atomic delete from all 3 indexes)."""
        pass
```

**Dependencies:**
- Requires: `PartitionConfig`, `SemanticIndex`, `ASTIndex`, `GraphIndex`
- Provides: Partition-level search, health checks, repository management
- Uses: `IncrementalIndexer`, `RepositoryTracker`

**Error Handling:**
- Repository not found in partition → Raise ValueError
- Sub-index initialization failure → Mark partition unhealthy, report in health check
- Incremental rebuild failure → Rollback changes, mark repo as `sync_failed`

---

### 2.3 Component: RepositoryTracker

**Purpose:** Track indexing state for each repository to enable incremental updates.

**Responsibilities:**
- Store commit hash, last indexed timestamp, file count, status per repository
- Detect changed files via Git diff
- Provide query API for repository state
- Update state atomically after successful index operation

**Requirements Satisfied:**
- FR-003: Repository State Tracking
- FR-004: Incremental Per-Repository Updates (provides change detection)
- NFR-R4: Atomic Updates (state updated only after success)

**Public Interface:**
```python
class RepositoryTracker:
    def __init__(self, db_path: Path):
        """Initialize tracker with DuckDB connection."""
        self.conn = duckdb.connect(str(db_path))
        self._create_tables()
    
    def get_state(self, repo_name: str) -> Optional[RepositoryState]:
        """Retrieve current state for repository."""
        pass
    
    def get_changed_files(self, repo_config: RepositoryConfig) -> List[Path]:
        """Detect changed files since last index via Git diff."""
        pass
    
    def mark_indexed(self, repo_name: str, commit_hash: str, file_count: int):
        """Atomically update state after successful index."""
        pass
    
    def mark_failed(self, repo_name: str, error: str):
        """Mark repository as sync_failed with error message."""
        pass
```

**Schema:**
```sql
CREATE TABLE repository_state (
    repo_name TEXT PRIMARY KEY,
    partition TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    last_indexed_at TIMESTAMP NOT NULL,
    file_count INTEGER NOT NULL,
    status TEXT NOT NULL,  -- 'indexed', 'sync_failed', 'pending'
    error_message TEXT
);
```

**Dependencies:**
- Requires: DuckDB, GitPython (for diff)
- Provides: Repository state queries, change detection
- Used by: `IncrementalIndexer`, `CodePartition`

**Error Handling:**
- Git operation failure → Log error, return empty changed files list
- Database write failure → Raise exception, don't update state
- Stale state (no prior index) → Return all files as changed

---

### 2.4 Component: RepositorySyncer

**Purpose:** Handle Git operations for repository synchronization.

**Responsibilities:**
- Clone remote repositories on first indexing
- Pull updates for existing repositories
- Support sparse checkout for large repositories
- Handle authentication via SSH keys or environment variables
- Gracefully handle Git errors without blocking other repositories

**Requirements Satisfied:**
- FR-007: Git Repository Synchronization
- NFR-R1: Graceful Parse Error Handling (Git errors don't block other repos)
- NFR-ST1: Total Disk Usage (sparse checkout reduces disk usage)

**Public Interface:**
```python
class RepositorySyncer:
    def __init__(self, base_path: Path):
        """Initialize syncer with base path for clones."""
        self.base_path = base_path
    
    def sync_repository(self, repo_config: RepositoryConfig) -> SyncResult:
        """Clone or pull repository, return new commit hash."""
        pass
    
    def clone(self, url: str, target_path: Path, sparse_paths: List[str]) -> str:
        """Clone repository with optional sparse checkout."""
        pass
    
    def pull(self, repo_path: Path) -> str:
        """Pull latest changes, return new commit hash."""
        pass
    
    def get_head_commit(self, repo_path: Path) -> str:
        """Get current HEAD commit hash."""
        pass
```

**Dependencies:**
- Requires: GitPython, filesystem access
- Provides: Repository sync operations
- Used by: `IncrementalIndexer`, `CodePartition`

**Error Handling:**
- Clone failure (network, auth) → Log error, raise SyncFailure exception
- Pull failure (merge conflicts) → Log error, use existing state, mark as `sync_failed`
- Sparse checkout not supported → Fall back to full clone, log warning
- Authentication failure → Provide actionable error with SSH key instructions

---

### 2.5 Component: IncrementalIndexer

**Purpose:** Update indexes efficiently by detecting and reprocessing only changed files.

**Responsibilities:**
- Detect changed files via `RepositoryTracker`
- Parse changed files once with Tree-sitter
- Extract data for all 3 indexes from single AST parse
- Atomically delete old data and insert new data across all 3 indexes
- Update `RepositoryTracker` state after successful indexing

**Requirements Satisfied:**
- FR-004: Incremental Per-Repository Updates
- NFR-P4: Incremental Update Performance (< 5 seconds for < 10 files)
- Parse-Once-Index-Thrice architectural decision

**Public Interface:**
```python
class IncrementalIndexer:
    def __init__(self, partition: CodePartition, tracker: RepositoryTracker, syncer: RepositorySyncer):
        """Initialize indexer with partition, tracker, syncer."""
        self.partition = partition
        self.tracker = tracker
        self.syncer = syncer
    
    def update_repository(self, repo_config: RepositoryConfig) -> RebuildStats:
        """Incrementally update single repository."""
        pass
    
    def update_file(self, file_path: Path, repo_config: RepositoryConfig):
        """Update single file across all 3 indexes (parse-once-index-thrice)."""
        pass
    
    def delete_repository(self, repo_name: str):
        """Atomically delete all data for repository from all 3 indexes."""
        pass
```

**Internal Flow:**
```python
def update_repository(self, repo_config):
    # 1. Git sync
    new_commit = self.syncer.sync_repository(repo_config)
    
    # 2. Detect changed files
    changed_files = self.tracker.get_changed_files(repo_config)
    
    # 3. Parse once, index thrice
    for file_path in changed_files:
        ast = parse_file(file_path)  # Tree-sitter parse
        
        # Extract data for all 3 indexes from single AST
        chunks = extract_semantic_chunks(ast, file_path, repo_config)
        nodes = extract_ast_nodes(ast, file_path, repo_config)
        symbols, edges = extract_graph_data(ast, file_path, repo_config)
        
        # Delete old data (atomic across all 3 indexes)
        self.partition.semantic.delete_chunks(file_path=file_path)
        self.partition.ast.delete_nodes(file_path=file_path)
        self.partition.graph.delete_symbols(file_path=file_path)
        
        # Insert new data (atomic across all 3 indexes)
        self.partition.semantic.add_chunks(chunks)
        self.partition.ast.add_nodes(nodes)
        self.partition.graph.add_symbols(symbols)
        self.partition.graph.add_relationships(edges)
    
    # 4. Update tracker state
    self.tracker.mark_indexed(repo_config.name, new_commit, len(changed_files))
```

**Dependencies:**
- Requires: `CodePartition`, `RepositoryTracker`, `RepositorySyncer`, Tree-sitter parser, `UniversalASTChunker`
- Provides: Incremental update operations
- Used by: `CodePartition`, `PartitionManager`

**Error Handling:**
- Parse failure → Skip file, log warning, continue with other files (NFR-R1)
- Index operation failure → Rollback all 3 indexes, don't update tracker state (NFR-R4)
- Git sync failure → Skip repository, mark as `sync_failed`, continue with other repos

---

### 2.6 Component: PartitionManager

**Purpose:** Manage partition lifecycle (CRUD operations) with validation and archival.

**Responsibilities:**
- Create new partitions (detect from config, init directories and tables)
- Update partitions (add/remove repositories)
- Delete partitions (soft delete with archival, optional hard delete)
- Detect orphaned data at startup
- Validate partition configuration

**Requirements Satisfied:**
- FR-010: Partition Lifecycle Management (CRUD)
- NFR-R3: Rollback Capability (soft delete with archival)
- NFR-O1: Startup Validation (orphaned data detection)
- NFR-O4: Config Validation

**Public Interface:**
```python
class PartitionManager:
    def __init__(self, base_path: Path, config: CodeIndexConfig):
        """Initialize manager with base path and config."""
        self.base_path = base_path
        self.config = config
    
    def validate_config(self) -> List[ValidationError]:
        """Validate partition config (paths, no duplicates, valid names)."""
        pass
    
    def create_partition(self, partition_name: str, partition_config: PartitionConfig):
        """Create new partition (dirs, tables, full build)."""
        pass
    
    def delete_partition(self, partition_name: str, hard_delete: bool = False):
        """Delete partition (soft delete archives to .archive/, hard delete removes permanently)."""
        pass
    
    def detect_orphaned_data(self) -> List[str]:
        """Detect index data without corresponding config entry."""
        pass
    
    def restore_partition(self, partition_name: str, timestamp: str):
        """Restore partition from .archive/{partition}_{timestamp}/."""
        pass
```

**Dependencies:**
- Requires: `CodeIndexConfig`, filesystem access
- Provides: Partition CRUD operations
- Uses: `CodePartition`, `IncrementalIndexer`

**Error Handling:**
- Invalid config → Return list of ValidationErrors, don't proceed
- Create failure (disk full) → Raise exception, cleanup partial state
- Delete failure (locked files) → Log error, provide manual cleanup instructions
- Orphaned data → Log warning, provide cleanup command, don't auto-delete

---

### 2.7 Component Interactions

**Interaction Diagram:**

```
┌───────────────┐
│  CodeIndex    │ (MCP Tool: pos_search_project)
└───────┬───────┘
        │ routes to
        ▼
┌────────────────────────────────────────┐
│  CodePartition (primary/instrumentors) │
└───┬─────────────┬──────────────┬───────┘
    │             │              │
    ▼             ▼              ▼
┌──────────┐ ┌─────────┐ ┌────────────┐
│Semantic  │ │AST Index│ │Graph Index │
│Index     │ │(DuckDB) │ │(DuckDB)    │
│(LanceDB) │ └─────────┘ └────────────┘
└──────────┘

Incremental Update Flow:
┌──────────────┐
│CodePartition │
└──────┬───────┘
       │ triggers
       ▼
┌─────────────────┐  uses  ┌──────────────┐
│IncrementalIndexer│───────>│RepositorySyncer│ (Git ops)
└────────┬────────┘        └──────────────┘
         │ uses
         ▼
┌──────────────────┐
│RepositoryTracker │ (change detection)
└──────────────────┘
```

**Key Interactions:**

| From Component | To Component | Method | Purpose |
|----------------|--------------|--------|---------|
| CodeIndex | CodePartition | `search()` | Route query to partition based on filters |
| CodeIndex | CodePartition | `health_check()` | Aggregate partition health |
| CodePartition | SemanticIndex | `search()` | Execute semantic search |
| CodePartition | ASTIndex | `search()` | Execute AST pattern search |
| CodePartition | GraphIndex | `search()` | Execute graph traversal |
| CodePartition | IncrementalIndexer | `update_repository()` | Trigger incremental update |
| IncrementalIndexer | RepositorySyncer | `sync_repository()` | Pull latest changes |
| IncrementalIndexer | RepositoryTracker | `get_changed_files()` | Detect files to update |
| IncrementalIndexer | SemanticIndex, ASTIndex, GraphIndex | `delete_chunks()`, `add_chunks()` | Atomic update across all 3 indexes |
| PartitionManager | CodePartition | `create()`, `delete()` | Manage partition lifecycle |
| PartitionManager | IncrementalIndexer | `rebuild_full()` | Trigger full rebuild for new partition |

---

### 2.8 Module Organization

**Directory Structure:**

```
ouroboros/subsystems/rag/code/
├── __init__.py
├── code_index.py          # CodeIndex (top-level)
├── partition.py           # CodePartition
├── tracker.py             # RepositoryTracker
├── syncer.py              # RepositorySyncer
├── indexer.py             # IncrementalIndexer
├── manager.py             # PartitionManager
├── semantic/              # SemanticIndex (existing, enhanced)
│   └── semantic.py
├── ast_index/             # ASTIndex (existing, enhanced)
│   └── ast.py
├── graph/                 # GraphIndex (existing, enhanced)
│   └── graph.py
└── chunking/              # UniversalASTChunker (existing from previous work)
    └── ast_chunker.py
```

**Dependency Rules:**
- No circular imports (dependency graph flows top-down)
- `CodeIndex` depends on `CodePartition`
- `CodePartition` depends on `SemanticIndex`, `ASTIndex`, `GraphIndex`
- `IncrementalIndexer` depends on all sub-indexes but not vice versa
- Indexes are independent of each other (no cross-index dependencies)
- All components depend on config models (`CodeIndexConfig`, `PartitionConfig`)

**Import Guidelines:**
- Use absolute imports: `from ouroboros.subsystems.rag.code.partition import CodePartition`
- Type hints in docstrings to avoid circular import issues
- Dependency injection: pass dependencies via constructors, not global imports

---

## 3. API Specifications

### 3.1 MCP Tool API: pos_search_project (Enhanced)

**Purpose:** Unified search API exposed to AI agents via MCP, now with multi-repo filtering.

**Existing Actions (Enhanced with Filters):**
- `search_code`: Semantic search (vector + FTS + RRF)
- `search_ast`: AST structural pattern search
- `find_callers`: Find functions that call a symbol
- `find_dependencies`: Find functions that a symbol calls
- `find_call_paths`: Find call chain between two symbols

**New Filter Parameters:**

```python
def pos_search_project(
    action: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    n_results: int = 5,
    max_depth: int = 10,
    method: str = "hybrid"
) -> Dict[str, Any]:
    """
    Unified search with multi-repo filtering.
    
    Args:
        action: Search operation (search_code, search_ast, find_callers, etc.)
        query: Search query or symbol name
        filters: Optional filtering by partition/repo/provider
            - partition: str (e.g., "primary", "instrumentors")
            - repo_name: str (e.g., "python-sdk")
            - provider: str (e.g., "opentelemetry", "openlit")
        n_results: Number of results to return
        max_depth: Maximum traversal depth for graph queries
        method: Search method (hybrid, vector, fts)
    
    Returns:
        {
            "status": "success",
            "action": str,
            "results": List[Dict],
            "count": int,
            "metadata": {
                "partition": str,
                "repo_name": str,
                "query_time_ms": float
            }
        }
    """
    pass
```

**Filter Examples:**

```python
# Search only in instrumentors partition
pos_search_project(
    action="search_code",
    query="span.set_attribute http attributes",
    filters={"partition": "instrumentors"}
)

# Search in specific repository
pos_search_project(
    action="search_ast",
    query="set_attribute call with string literal",
    filters={"repo_name": "fastapi-instrumentation"}
)

# Search by provider
pos_search_project(
    action="search_code",
    query="LLM instrumentation patterns",
    filters={"provider": "openlit"}
)

# Combined filters
pos_search_project(
    action="find_callers",
    query="process_span",
    filters={
        "partition": "instrumentors",
        "provider": "opentelemetry"
    }
)
```

**Response Format (Enhanced with Metadata):**

```python
{
    "status": "success",
    "action": "search_code",
    "results": [
        {
            "chunk_id": "abc123",
            "content": "span.set_attribute('http.method', request.method)",
            "file_path": "../vendor/fastapi-instrumentor/instrumentation.py",
            "repo_name": "fastapi-instrumentation",  # NEW
            "partition": "instrumentors",            # NEW
            "provider": "opentelemetry",             # NEW
            "start_line": 45,
            "relevance_score": 0.89,
            "chunk_type": "function",
            "symbols": ["_instrument_request"]
        }
    ],
    "count": 1,
    "metadata": {
        "partition": "instrumentors",
        "query_time_ms": 145.3,
        "total_chunks_searched": 324000
    }
}
```

**Requirements Satisfied:**
- FR-005: Cross-Repository Query Filtering
- NFR-P1/P2: Query Latency (partition routing for performance)

---

### 3.2 Extraction Workflow APIs

**Purpose:** Structured query workflows for semantic convention extraction.

#### 3.2.1 Extract Span Attributes

```python
def extract_span_attributes(repo_name: str) -> AttributeReport:
    """
    Extract all span.set_attribute() calls from instrumentor.
    
    Args:
        repo_name: Repository name to analyze
    
    Returns:
        AttributeReport with:
        - attributes: List[AttributeSpec]
        - dynamic_patterns: List[DynamicAttributePattern]
        - total_count: int
    """
    results = pos_search_project(
        action="search_ast",
        query="span.set_attribute",
        filters={"repo_name": repo_name}
    )
    
    attributes = []
    for result in results:
        # Parse AST result to extract:
        # - Attribute key (first argument)
        # - Value source (second argument)
        # - Context (function, file, line)
        attr = parse_set_attribute_call(result)
        attributes.append(attr)
    
    return AttributeReport(
        attributes=attributes,
        dynamic_patterns=detect_dynamic_patterns(results),
        total_count=len(attributes)
    )
```

**Output Schema:**

```python
@dataclass
class AttributeSpec:
    key: str                    # e.g., "http.method"
    value_type: str             # "variable", "literal", "dynamic"
    value_source: str           # e.g., "request.method"
    file_path: str
    line_number: int
    function_name: str
    example_value: Optional[str] = None
```

#### 3.2.2 Extract Span Naming Patterns

```python
def extract_span_naming(repo_name: str) -> SpanNamingReport:
    """
    Extract span naming patterns from start_span() calls.
    
    Returns:
        SpanNamingReport with:
        - pattern: str (e.g., "langchain.{class}.{method}")
        - examples: List[str]
        - source_locations: List[Location]
    """
    results = pos_search_project(
        action="search_ast",
        query="start_span name argument",
        filters={"repo_name": repo_name}
    )
    
    # Analyze patterns
    pattern = infer_naming_pattern(results)
    examples = extract_example_names(results)
    
    return SpanNamingReport(
        pattern=pattern,
        examples=examples,
        source_locations=[r["file_path"] for r in results]
    )
```

#### 3.2.3 Export to YAML/JSON

```python
def export_conventions(report: ConventionReport, format: str = "yaml") -> str:
    """
    Export extraction results as YAML or JSON.
    
    Args:
        report: ConventionReport with attributes, naming, events
        format: "yaml" or "json"
    
    Returns:
        Formatted string ready for file write
    """
    if format == "yaml":
        return yaml.dump(report.to_dict(), default_flow_style=False)
    elif format == "json":
        return json.dumps(report.to_dict(), indent=2)
```

**Requirements Satisfied:**
- FR-008: Semantic Convention Extraction Workflows
- FR-009: Machine-Readable Output Generation

---

### 3.3 Internal APIs (Component Interfaces)

#### 3.3.1 CodeIndex API

```python
class CodeIndex:
    def search(
        self, 
        query: str, 
        action: str, 
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Route search to partition(s) based on filters."""
        
    def health_check(self) -> HealthStatus:
        """Aggregate health from all partitions."""
        
    def rebuild_partition(self, partition_name: str):
        """Trigger full rebuild of specific partition."""
```

#### 3.3.2 CodePartition API

```python
class CodePartition:
    def search(self, query: str, action: str, **kwargs) -> List[Dict]:
        """Route to Semantic/AST/Graph based on action."""
        
    def add_repository(self, repo_config: RepositoryConfig):
        """Add new repo (incremental index)."""
        
    def remove_repository(self, repo_name: str):
        """Remove repo (atomic delete from all 3 indexes)."""
        
    def health_check(self) -> HealthStatus:
        """Fractal check of 3 sub-indexes."""
```

#### 3.3.3 RepositoryTracker API

```python
class RepositoryTracker:
    def get_changed_files(self, repo_config: RepositoryConfig) -> List[Path]:
        """Detect changed files via Git diff."""
        
    def mark_indexed(self, repo_name: str, commit_hash: str, file_count: int):
        """Update state after successful index."""
```

---

## 4. Data Models

### 4.1 Configuration Models (Pydantic)

#### 4.1.1 PartitionConfig

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class RepositoryConfig(BaseModel):
    """Configuration for a single repository."""
    name: str = Field(..., description="Unique repository name")
    path: Optional[str] = Field(None, description="Local path (if exists)")
    url: Optional[str] = Field(None, description="Remote Git URL")
    provider: str = Field(..., description="Provider (honeyhive, opentelemetry, openlit, traceloop, arize, local)")
    sparse_paths: List[str] = Field(default_factory=list, description="Sparse checkout paths (subdirectories only)")
    enabled: bool = Field(default=True, description="Enable/disable indexing")

class PerformanceTargets(BaseModel):
    """Performance targets for partition indexes."""
    semantic: Dict[str, int] = Field(default={"p95_ms": 150}, description="Semantic index p95 latency")
    ast: Dict[str, int] = Field(default={"p95_ms": 50}, description="AST index p95 latency")
    graph: Dict[str, int] = Field(default={"p95_ms": 100}, description="Graph index p95 latency")

class PartitionConfig(BaseModel):
    """Configuration for a partition."""
    name: str = Field(..., description="Human-readable partition name")
    repositories: List[RepositoryConfig] = Field(..., description="Repositories in partition")
    performance_targets: PerformanceTargets = Field(default_factory=PerformanceTargets)
    graph_cross_repo: bool = Field(True, description="Enable cross-repo call graph edges")

class CodeIndexConfig(BaseModel):
    """Configuration for entire code index."""
    partitions: Dict[str, PartitionConfig] = Field(..., description="Partition definitions (key = partition_name)")
    chunking_strategy: str = Field(default="ast", description="Chunking strategy (ast or line)")
    # ... existing fields from AST-Aware Chunking spec
```

**Example mcp.yaml:**

```yaml
indexes:
  code:
    chunking_strategy: "ast"
    partitions:
      primary:
        name: "Primary Code"
        repositories:
          - name: "praxis-os"
            path: "/Users/josh/src/github.com/honeyhiveai/praxis-os/ouroboros/"
            provider: "local"
          - name: "python-sdk"
            url: "https://github.com/honeyhiveai/python-sdk"
            provider: "honeyhive"
        performance_targets:
          semantic: {p95_ms: 50}
          ast: {p95_ms: 50}
          graph: {p95_ms: 100}
        graph_cross_repo: true
      
      instrumentors:
        name: "OpenTelemetry Instrumentors"
        repositories:
          - name: "openai-instrumentation"
            url: "https://github.com/open-telemetry/opentelemetry-python-contrib"
            sparse_paths: ["instrumentation/opentelemetry-instrumentation-openai"]
            provider: "opentelemetry"
          - name: "langchain-instrumentation"
            url: "https://github.com/traceloop/openllmetry"
            sparse_paths: ["packages/opentelemetry-instrumentation-langchain"]
            provider: "traceloop"
        performance_targets:
          semantic: {p95_ms: 200}
          ast: {p95_ms: 75}
          graph: {p95_ms: 150}
        graph_cross_repo: false
```

---

### 4.2 Database Schemas

#### 4.2.1 SemanticIndex (LanceDB)

**Enhanced Chunk Schema:**

```python
{
    "chunk_id": str,              # Unique identifier (hash of content + metadata)
    "content": str,               # Source code text
    "file_path": str,             # Relative path within repository
    "start_line": int,
    "end_line": int,
    "chunk_type": str,            # "function", "class", "method", "module"
    "symbols": List[str],         # Function/class names
    "token_count": int,
    "import_ratio": float,
    "import_penalty": float,
    
    # NEW: Multi-repo metadata
    "partition": str,             # "primary", "instrumentors"
    "repo_name": str,             # "python-sdk", "fastapi-instrumentation"
    "provider": str,              # "honeyhive", "opentelemetry", "openlit", etc.
    
    # Vector embedding (512-dim CodeBERT)
    "embedding": List[float]      # Vector for semantic search
}
```

**Indexes:**
- Primary key: `chunk_id`
- Vector index: `embedding` (IVF_PQ for fast ANN search)
- Full-text index: `content` (built-in Tantivy FTS)
- Metadata filters: `partition`, `repo_name`, `provider`, `chunk_type`

---

#### 4.2.2 ASTIndex (DuckDB `ast_nodes` table)

**Enhanced Schema:**

```sql
CREATE TABLE ast_nodes (
    node_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    node_type TEXT NOT NULL,         -- e.g., "function_definition", "call_expression"
    node_text TEXT NOT NULL,
    parent_id TEXT,
    
    -- NEW: Multi-repo metadata
    partition TEXT NOT NULL,
    repo_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    
    -- Indexes
    INDEX idx_node_type (node_type),
    INDEX idx_file_path (file_path),
    INDEX idx_partition_repo (partition, repo_name)
);
```

**Query Pattern Example:**

```sql
-- Find all set_attribute calls in instrumentors partition
SELECT node_id, file_path, start_line, node_text, repo_name
FROM ast_nodes
WHERE partition = 'instrumentors'
  AND node_type = 'call_expression'
  AND node_text LIKE '%set_attribute%';
```

---

#### 4.2.3 GraphIndex (DuckDB `symbols` and `relationships` tables)

**Enhanced Symbols Schema:**

```sql
CREATE TABLE symbols (
    symbol_id TEXT PRIMARY KEY,
    symbol_name TEXT NOT NULL,
    symbol_type TEXT NOT NULL,       -- "function", "class", "method"
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    
    -- NEW: Multi-repo metadata
    partition TEXT NOT NULL,
    repo_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    
    -- Indexes
    INDEX idx_symbol_name (symbol_name),
    INDEX idx_partition_repo (partition, repo_name)
);
```

**Enhanced Relationships Schema:**

```sql
CREATE TABLE relationships (
    relationship_id TEXT PRIMARY KEY,
    caller_id TEXT NOT NULL,         -- Foreign key to symbols(symbol_id)
    callee_id TEXT NOT NULL,         -- Foreign key to symbols(symbol_id)
    relationship_type TEXT NOT NULL, -- "calls", "imports", "inherits"
    
    -- NEW: Multi-repo metadata for cross-repo edge filtering
    caller_repo TEXT NOT NULL,
    callee_repo TEXT NOT NULL,
    
    FOREIGN KEY (caller_id) REFERENCES symbols(symbol_id),
    FOREIGN KEY (callee_id) REFERENCES symbols(symbol_id),
    
    -- Indexes
    INDEX idx_caller (caller_id),
    INDEX idx_callee (callee_id),
    INDEX idx_cross_repo (caller_repo, callee_repo)
);
```

**Cross-Repo Query Pattern:**

```sql
-- Find callers of symbol, respecting graph_cross_repo config
WITH RECURSIVE call_chain AS (
    -- Base case: direct callers
    SELECT r.caller_id, s.symbol_name, s.repo_name, 1 AS depth
    FROM relationships r
    JOIN symbols s ON r.caller_id = s.symbol_id
    WHERE r.callee_id = :target_symbol_id
      AND s.partition = :partition
      AND (:allow_cross_repo = TRUE OR r.caller_repo = r.callee_repo)
    
    UNION ALL
    
    -- Recursive case: callers of callers
    SELECT r.caller_id, s.symbol_name, s.repo_name, cc.depth + 1
    FROM relationships r
    JOIN symbols s ON r.caller_id = s.symbol_id
    JOIN call_chain cc ON r.callee_id = cc.caller_id
    WHERE cc.depth < :max_depth
      AND (:allow_cross_repo = TRUE OR r.caller_repo = r.callee_repo)
)
SELECT * FROM call_chain;
```

---

#### 4.2.4 RepositoryTracker Schema (DuckDB `repository_state` table)

```sql
CREATE TABLE repository_state (
    repo_name TEXT PRIMARY KEY,
    partition TEXT NOT NULL,
    commit_hash TEXT NOT NULL,
    last_indexed_at TIMESTAMP NOT NULL,
    file_count INTEGER NOT NULL,
    status TEXT NOT NULL,           -- 'indexed', 'sync_failed', 'pending'
    error_message TEXT,
    
    INDEX idx_partition (partition),
    INDEX idx_status (status)
);
```

---

### 4.3 Runtime Data Structures

#### 4.3.1 RepositoryState

```python
@dataclass
class RepositoryState:
    repo_name: str
    partition: str
    commit_hash: str
    last_indexed_at: datetime
    file_count: int
    status: str  # 'indexed', 'sync_failed', 'pending'
    error_message: Optional[str] = None
```

#### 4.3.2 SyncResult

```python
@dataclass
class SyncResult:
    success: bool
    new_commit: Optional[str]
    error: Optional[str]
    changed_files: List[Path]
```

#### 4.3.3 RebuildStats

```python
@dataclass
class RebuildStats:
    files_updated: int = 0
    files_added: int = 0
    files_deleted: int = 0
    parse_errors: int = 0
    total_time_ms: float = 0.0
```

#### 4.3.4 HealthStatus (Fractal ComponentDescriptor)

```python
@dataclass
class HealthStatus:
    healthy: bool
    name: str
    components: Dict[str, HealthStatus]  # Recursive for fractal hierarchy
    metrics: Dict[str, Any] = None
    error: Optional[str] = None
```

---

## 5. Security Considerations

### 5.1 Git Credentials

**Requirement:** FR-007 mandates authentication via SSH keys or environment variables, NOT inline in config files.

**Implementation:**

```python
# ✅ CORRECT: SSH keys (default Git behavior)
repo_config = RepositoryConfig(
    name="private-repo",
    url="git@github.com:honeyhiveai/private-sdk.git",  # SSH URL
    provider="honeyhive"
)

# ✅ CORRECT: HTTPS with environment variable
import os
os.environ["GIT_ASKPASS"] = "/path/to/credential/helper"
repo_config = RepositoryConfig(
    name="private-repo",
    url="https://github.com/honeyhiveai/private-sdk.git",
    provider="honeyhive"
)

# ❌ INCORRECT: Hardcoded credentials
repo_config = RepositoryConfig(
    url="https://user:password@github.com/..."  # NEVER DO THIS
)
```

**Validation:**
- Config validator rejects URLs with embedded credentials
- Provide actionable error: "Use SSH keys or environment variables for authentication"

**Requirements Satisfied:** NFR-S1 (implicit, credential security)

---

### 5.2 Path Traversal Prevention

**Requirement:** Prevent malicious config from accessing files outside workspace.

**Implementation:**

```python
def validate_repository_path(path: str, workspace_root: Path) -> Path:
    """Validate path to prevent directory traversal."""
    resolved = Path(path).resolve()
    workspace_resolved = workspace_root.resolve()
    
    # Ensure path is within workspace or explicitly allowed locations
    if not (resolved.is_relative_to(workspace_resolved) or 
            resolved.is_relative_to(Path.home() / "src")):
        raise ValueError(
            f"Path {path} is outside allowed directories. "
            f"Allowed: {workspace_resolved}, ~/src/"
        )
    
    return resolved
```

**Validation:**
- All paths validated on config load
- Reject paths with `..` components attempting to escape workspace
- Log validation errors with actionable remediation

**Requirements Satisfied:** NFR-O4 (Config Validation)

---

### 5.3 Sparse Checkout (Disk Exposure Limitation)

**Requirement:** NFR-ST1 mandates disk usage < 3GB, sparse checkout reduces exposure.

**Implementation:**

```python
def sparse_clone(url: str, target: Path, sparse_paths: List[str]):
    """Clone with sparse checkout (only specified subdirectories)."""
    repo = git.Repo.init(target)
    repo.git.config("core.sparseCheckout", "true")
    
    # Write sparse-checkout file
    sparse_file = target / ".git" / "info" / "sparse-checkout"
    sparse_file.write_text("\n".join(sparse_paths))
    
    # Clone with sparse checkout active
    origin = repo.create_remote("origin", url)
    origin.fetch()
    repo.git.checkout("main")
```

**Benefits:**
- Reduces disk usage (only index relevant subdirectories)
- Limits exposure to unnecessary code (e.g., tests, docs, examples)
- Faster initial clone

---

### 5.4 Error Message Safety

**Requirement:** Error messages must not leak sensitive paths or credentials.

**Implementation:**

```python
def safe_error_message(error: Exception, repo_name: str) -> str:
    """Sanitize error messages to remove sensitive info."""
    msg = str(error)
    
    # Remove absolute paths
    msg = re.sub(r'/Users/[^/]+/.*?/', '<workspace>/', msg)
    
    # Remove URLs with potential credentials
    msg = re.sub(r'https://[^@]+@', 'https://<credentials>@', msg)
    
    return f"Repository {repo_name}: {msg}"
```

---

## 6. Performance Optimization

### 6.1 Partition Routing (Query Performance)

**Strategy:** Route queries to appropriate partition(s) based on filters to minimize chunks searched.

**Implementation:**

```python
def search(self, query: str, action: str, filters: Optional[Dict] = None):
    """Route to partition(s) based on filters."""
    if filters and "partition" in filters:
        # Route to specific partition
        partition_name = filters["partition"]
        return self.partitions[partition_name].search(query, action, **filters)
    else:
        # Search all partitions, aggregate results
        all_results = []
        for partition in self.partitions.values():
            results = partition.search(query, action, **filters)
            all_results.extend(results)
        return sorted(all_results, key=lambda r: r["relevance_score"], reverse=True)
```

**Performance Impact:**
- Partition-specific query: Search only relevant chunks (e.g., 113K for primary vs. 437K total)
- Primary partition p95 < 50ms (NFR-P1)
- Instrumentors partition p95 < 200ms (NFR-P2)

**Requirements Satisfied:** NFR-P1, NFR-P2

---

### 6.2 Parse-Once-Index-Thrice

**Strategy:** Single Tree-sitter parse per file populates all 3 indexes.

**Performance Impact:**
- 3x faster than parsing 3 times separately
- Typical file (500 lines): Parse 150ms, extract 3 data structures 50ms → Total 200ms
- Alternative (parse 3x): Parse 150ms × 3 = 450ms
- **Speedup: 2.25x**

**Requirements Satisfied:** NFR-P4 (< 5 seconds for incremental updates)

---

### 6.3 Incremental Indexing

**Strategy:** Git diff to detect changed files, update only those files.

**Implementation:**

```python
changed_files = tracker.get_changed_files(repo_config)  # Git diff
# Only reprocess changed files, not entire repository
```

**Performance Impact:**
- Typical change: 5 files → 5 × 200ms = 1 second
- Full re-index: 1000 files → 1000 × 200ms = 200 seconds = 3.3 minutes
- **Speedup: 200x for typical changes**

**Requirements Satisfied:** NFR-P4

---

### 6.4 Sparse Checkout

**Strategy:** Clone only specified subdirectories for large instrumentor repos.

**Performance Impact:**
- Full repo: 10K files, 2GB
- Sparse (instrumentation/ only): 500 files, 100MB
- **Disk savings: 95%**
- **Clone time: 5x faster**

**Requirements Satisfied:** NFR-ST1 (< 2GB for instrumentors partition)

---

### 6.5 Concurrent Indexing (Future Optimization)

**Strategy:** Parallelize file parsing across CPU cores.

**Implementation (Future):**

```python
from concurrent.futures import ProcessPoolExecutor

def update_files_parallel(files: List[Path]):
    with ProcessPoolExecutor(max_workers=4) as executor:
        executor.map(update_single_file, files)
```

**Performance Impact:**
- 4 cores: 4x speedup for full index build
- Cold start: 10 minutes → 2.5 minutes

**Requirements Satisfied:** NFR-P5 (< 10 minutes cold start for 270 instrumentors)

---

## 7. Summary

### 7.1 Deliverables

This technical specification defines:

1. **Architecture:** Partition-based modular monolith with dynamic discovery
2. **Components:** 6 core components (CodeIndex, CodePartition, RepositoryTracker, RepositorySyncer, IncrementalIndexer, PartitionManager)
3. **APIs:** Enhanced `pos_search_project` with multi-repo filtering, extraction workflows
4. **Data Models:** Pydantic config models, enhanced database schemas (LanceDB + DuckDB)
5. **Security:** Git credential handling, path validation, sparse checkout
6. **Performance:** Partition routing, parse-once-index-thrice, incremental indexing

### 7.2 Requirements Traceability

All 10 functional requirements (FR-001 through FR-010) and 22 non-functional requirements are addressed by the technical design.

### 7.3 Next Phase

**Phase 3 (Task Breakdown)** will decompose this design into implementation tasks with time estimates, dependencies, and acceptance criteria.

---
