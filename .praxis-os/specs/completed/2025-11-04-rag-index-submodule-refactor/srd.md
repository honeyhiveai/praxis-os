# Software Requirements Document

**Project:** RAG Index Submodule Refactor  
**Date:** 2025-11-04  
**Priority:** High  
**Category:** Enhancement (Architectural Refactoring)

---

## 1. Introduction

### 1.1 Purpose
This document defines the requirements for refactoring the RAG index system to use a submodule-per-index pattern, addressing inconsistent abstractions and enabling scalable addition of new indexes.

### 1.2 Scope
This refactor will reorganize existing RAG indexes (standards, code) into self-contained submodules with uniform interfaces, consolidate database architecture to LanceDB + DuckDB only (eliminating SQLite), implement file locking for corruption prevention, and establish a pattern for easily adding future indexes (project_docs, dependency_docs).

---

## 2. Business Goals

### Goal 1: Enable Independent Index Evolution

**Objective:** Allow indexes to evolve independently without requiring changes to core orchestration (IndexManager) or affecting other indexes.

**Success Metrics:**
- **Index Addition Time**: Current ~4 hours (modify IndexManager + add special cases) → Target <30 minutes (create submodule + add to registry)
- **Cross-Index Coupling**: Current 4+ special case branches in IndexManager → Target 0 special cases
- **Regression Risk**: Current High (changes affect all indexes) → Target None (isolated changes)

**Business Impact:**
- AI/human developers can extend search capabilities faster
- Reduces QA burden (isolated changes mean smaller test surface)
- Enables parallel development (different developers can work on different indexes without conflicts)

### Goal 2: Eliminate Index Corruption from Concurrent Access

**Objective:** Prevent index corruption caused by manual rebuild scripts running while MCP server is operating.

**Success Metrics:**
- **Corruption Incidents**: Current ~2-3 per week (observed from logs) → Target 0 per month
- **Index Rebuild Success Rate**: Current ~85% (corruption requires re-rebuilds) → Target 100%
- **User-Reported "Index Broken" Issues**: Current 1-2 per week → Target 0 per month

**Business Impact:**
- Users experience "just works" reliability (no manual index rebuilds needed)
- Reduces support burden (no troubleshooting corrupted indexes)
- Server auto-repairs on startup (operational resilience)

### Goal 3: Simplify Database Architecture

**Objective:** Consolidate to two database technologies (LanceDB + DuckDB) by eliminating SQLite, reducing complexity and maintenance burden.

**Success Metrics:**
- **Database Technologies**: Current 3 (LanceDB, DuckDB, SQLite) → Target 2 (LanceDB, DuckDB)
- **Database Connection Code Duplication**: Current ~200 lines duplicated across 3 files → Target <50 lines (shared utilities)
- **Index Build Time**: Current ~2-3 minutes → Target ~1-2 minutes (single-pass DuckDB vs SQLite+DuckDB)

**Business Impact:**
- Simpler mental model for developers (2 databases, clear separation: semantic=LanceDB, structural=DuckDB)
- Reduced dependency count (one less database to maintain/update)
- Better performance (DuckDB recursive CTEs faster than SQLite for graph queries)

### Goal 4: Establish Predictable Discovery Patterns

**Objective:** Provide uniform entry point (`container.py`) for all indexes, enabling developers (AI and human) to quickly understand any index's capabilities.

**Success Metrics:**
- **Discovery Time**: Current "browse 3-4 files to understand" (~15 min) → Target "open container.py" (~2 min)
- **Pattern Consistency**: Current 2 patterns (standards all-in-one, code split 3-way) → Target 1 pattern (all use container.py)
- **Onboarding Time**: Current ~1 hour to understand index system → Target ~15 minutes (predictable structure)

**Business Impact:**
- Faster AI assistant comprehension (predictable patterns improve tool usage)
- Easier code reviews (reviewers know where to look)
- Reduced cognitive load (same pattern everywhere)

## 2.1 Supporting Documentation

The business goals above are informed by:
- **RAG Index Submodule Pattern Design Doc**: Documented inconsistent abstractions, corruption patterns from concurrent access, database architecture issues, and proposed submodule pattern with quantifiable improvements

See `supporting-docs/INDEX.md` for complete analysis and extracted insights.

---

## 3. User Stories


### Story 1: Discover Index Capabilities Predictably

**As a** AI developer implementing search features  
**I want to** find all capabilities of an index by opening a single predictable file (`container.py`)  
**So that** I can understand what an index does in 2 minutes instead of browsing 3-4 implementation files for 15 minutes

**Acceptance Criteria:**
- Given any index submodule (standards, code, project_docs, etc.)
- When I open `{index}/container.py`
- Then I see all public methods (search, build, update, health_check, get_stats) with clear signatures
- And I can understand index capabilities without reading implementation files

**Priority:** High

---

### Story 2: Add New Index Without Modifying Core

**As a** system architect extending RAG capabilities  
**I want to** add a new index (project_docs, dependency_docs) by creating a submodule and adding it to the registry  
**So that** I can extend search capabilities in 30 minutes without risking regression in existing indexes or requiring IndexManager changes

**Acceptance Criteria:**
- Given I want to add a new index type (e.g., "dependency_docs")
- When I create `rag/dependency_docs/` submodule with `__init__.py`, `container.py`, and implementation files
- And add one entry to `INDEX_REGISTRY` in `index_manager.py`
- And add configuration to `config/mcp.yaml`
- Then the new index is discovered, initialized, and operational
- And existing indexes (standards, code) are unaffected
- And no IndexManager logic changes required

**Priority:** Critical (Must-Have)

---

### Story 3: Prevent Index Corruption from Concurrent Rebuilds

**As a** human developer running manual rebuild scripts  
**I want to** receive clear error when MCP server is running and holding the index lock  
**So that** I don't corrupt indexes and waste 20-30 minutes debugging "lance error: Invalid manifest" failures

**Acceptance Criteria:**
- Given MCP server is running and holds a shared lock on standards index
- When I run `python rebuild_index.py --force` in terminal
- Then the script fails immediately with actionable error message
- And the error states: "MCP server is using the index, close Cursor first"
- And the error includes how to fix: "Close Cursor → wait 5 seconds → retry"
- And NO corruption occurs (index remains functional)

**Priority:** Critical (Must-Have)

---

### Story 4: Evolve Index Internals Independently

**As a** human developer maintaining the code index  
**I want to** refactor code index internals (combine AST+graph, optimize queries, change chunking strategy) without affecting IndexManager or tools  
**So that** I can improve index performance or fix bugs with zero risk to other parts of the system

**Acceptance Criteria:**
- Given code index currently uses `semantic.py` + `graph.py` (2 files, 2 databases)
- When I refactor internals (merge files, change database schema, optimize queries)
- And I maintain the `BaseIndex` interface (search, build, update, etc.)
- Then IndexManager continues to work without changes
- And Tools layer continues to work without changes
- And Other indexes (standards, project_docs) are unaffected
- And Tests only need updates for code index, not IndexManager

**Priority:** High

---

### Story 5: Query Index Without Corruption Failures

**As an** end user (AI/human) querying RAG indexes via MCP tools  
**I want** indexes to automatically detect and repair corruption without requiring manual intervention  
**So that** I experience "just works" reliability and never see "lance error: Invalid manifest" failures

**Acceptance Criteria:**
- Given standards index is corrupted (LanceDB manifest invalid)
- When I query via `pos_search_project(action="search_standards", query="...") `
- Then the index detects corruption automatically
- And the index rebuilds itself (acquires exclusive lock, re-chunks, re-embeds)
- And the search retries after rebuild completes
- And I receive valid search results within 60 seconds
- And corruption is logged (⚠️ warning) but doesn't surface as user error

**Priority:** High

---

### Story 6: Understand Database Architecture at a Glance

**As a** human developer onboarding to the RAG system  
**I want to** understand which database each index uses and why (semantic=LanceDB, structural=DuckDB)  
**So that** I can make informed decisions about query performance and data modeling in 5 minutes instead of reverse-engineering from 3 different database connection patterns

**Acceptance Criteria:**
- Given I'm reading the codebase to understand RAG architecture
- When I open `rag/base.py` or read architecture documentation
- Then I see clear statement: "2 databases: LanceDB (semantic: vector+FTS+scalar), DuckDB (structural: AST+graph+recursive CTEs)"
- And I see pattern: Simple indexes use LanceDB only, complex indexes use LanceDB+DuckDB
- And I see NO SQLite references (eliminated)
- And utilities (`lancedb_helpers.py`, `duckdb_helpers.py`) consolidate connection logic

**Priority:** Medium

---

## 3.1 Story Priority Summary

**Critical (Must-Have):**
- Story 2: Add New Index Without Modifying Core (enables scalability goal)
- Story 3: Prevent Index Corruption from Concurrent Rebuilds (eliminates primary corruption source)

**High Priority:**
- Story 1: Discover Index Capabilities Predictably (discoverability goal)
- Story 4: Evolve Index Internals Independently (independent evolution goal)
- Story 5: Query Index Without Corruption Failures (auto-repair reliability)

**Medium Priority:**
- Story 6: Understand Database Architecture at a Glance (simplified mental model)

## 3.2 Supporting Documentation

User needs from supporting documents:
- **RAG Index Submodule Pattern Design Doc**: Documented user pain points including 15-minute discovery time, 4-hour index addition time, corruption from manual rebuilds, and inconsistent patterns across indexes

See `supporting-docs/INDEX.md` for complete user need extraction from motivation and problem statement sections.

---

## 4. Functional Requirements


### FR-001: Uniform Container Entry Point

**Description:** The system shall provide a uniform entry point (`container.py`) for every index submodule, implementing the `BaseIndex` interface with all required methods (build, search, update, health_check, get_stats).

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- Every index submodule (standards, code, project_docs, dependency_docs) has `{submodule}/container.py` file
- Container class implements `BaseIndex` abstract interface with all 5 required methods
- `__init__.py` exports only the container class (pure export, no implementation)
- Container class name follows pattern: `{IndexName}Index` (e.g., `StandardsIndex`, `CodeIndex`)
- IndexManager imports from submodule root: `from ouroboros.subsystems.rag.standards import StandardsIndex`

---

### FR-002: Registry-Based Index Discovery

**Description:** The system shall use a registry pattern (`INDEX_REGISTRY`) to dynamically discover and initialize all configured indexes without special-case logic in IndexManager.

**Priority:** Critical

**Related User Stories:** Story 2

**Acceptance Criteria:**
- `INDEX_REGISTRY` dictionary maps index names to (module_path, class_name, description)
- IndexManager initialization iterates registry and dynamically imports/instantiates indexes
- Adding new index requires only: (1) create submodule, (2) add registry entry, (3) add config
- IndexManager contains zero special-case branches for specific indexes (no `if index_name == "ast"`)
- All indexes initialized with uniform signature: `IndexClass(config, base_path)`

---

### FR-003: File-Based Lock for Corruption Prevention

**Description:** The system shall implement file-based locking (fcntl on POSIX, stub on Windows) to prevent concurrent access to indexes from multiple processes (MCP server + manual rebuild scripts).

**Priority:** Critical

**Related User Stories:** Story 3

**Acceptance Criteria:**
- `IndexLockManager` utility class provides `acquire_shared()` and `acquire_exclusive()` methods
- MCP server acquires SHARED lock on index connection, holds for server lifetime
- Rebuild operations acquire EXCLUSIVE lock via context manager, released after rebuild
- Multiple processes can hold shared locks simultaneously (queries from stdio + http)
- Exclusive lock blocks all other access (shared and exclusive)
- Failed lock acquisition returns actionable error with how-to-fix guidance
- Lock files stored as `.{index_name}.lock` in index cache directory

---

### FR-004: Database Consolidation (LanceDB + DuckDB)

**Description:** The system shall use exactly two database technologies: LanceDB for semantic search (vector+FTS+scalar) and DuckDB for structural search (AST+graph+recursive CTEs), eliminating SQLite entirely.

**Priority:** High

**Related User Stories:** Story 6

**Acceptance Criteria:**
- LanceDB used for: vector embeddings, full-text search, scalar metadata indexes (domain, phase, language, file_path)
- DuckDB used for: AST symbols table, call graph relationships table, recursive CTEs for graph traversal
- Zero SQLite imports or connections in codebase
- Code index uses both databases: semantic.py (LanceDB), graph.py (DuckDB)
- Standards index uses one database: semantic.py (LanceDB only)
- Shared utilities: `LanceDBConnection`, `DuckDBConnection` in `rag/utils/` directory

---

### FR-005: Corruption Detection and Auto-Repair

**Description:** The system shall automatically detect index corruption at startup (health checks) and runtime (search errors), rebuild corrupted indexes without user intervention, and retry failed operations after repair.

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- Startup: `IndexManager.ensure_all_indexes_healthy()` runs health checks on all indexes
- Health check validates: (1) metadata exists, (2) functional queries work, (3) row counts reasonable
- Corruption patterns detected: "lance error", "invalid manifest", "corrupted", "external error", "not found"
- Auto-repair flow: detect corruption → acquire exclusive lock → rebuild → retry operation (once)
- Rebuild lock prevents concurrent rebuilds (`_rebuild_lock`, `_is_rebuilding` flag)
- Successful repair logged with ✅, failures logged with ❌ and actionable guidance
- User never sees corruption errors (auto-repaired transparently)

---

### FR-006: Shared Utility Modules (DRY)

**Description:** The system shall provide shared utility modules (`rag/utils/`) for common operations (LanceDB connection, DuckDB connection, embedding model loading, file change tracking) to eliminate code duplication across indexes.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- `LanceDBConnection` class: lazy initialization, connection pooling, table opening, error handling
- `EmbeddingModelLoader` class: class-level cache, lazy loading, handles ImportError gracefully
- `DuckDBConnection` class: lazy initialization, query execution, error handling
- `FileChangeTracker` class: tracks file hashes/mtimes, detects new/modified/deleted files
- All indexes use shared utilities (no duplicated connection code)
- Utilities handle errors with `ActionableError` (what failed, why, how to fix)

---

### FR-007: Independent Submodule Internals

**Description:** The system shall allow each index submodule to organize its internal implementation files freely (simple: 1 file, complex: N files) while maintaining uniform external interface via container.py.

**Priority:** High

**Related User Stories:** Story 4

**Acceptance Criteria:**
- Simple indexes (standards, project_docs): `container.py` delegates to single `semantic.py`
- Complex indexes (code): `container.py` orchestrates multiple files (`semantic.py`, `graph.py`)
- Internal file changes (merge, split, refactor) do NOT require IndexManager changes
- Internal file changes do NOT require tool layer changes
- IndexManager and tools import only from submodule root (`from rag.code import CodeIndex`)
- No direct imports of internal files (`from rag.code.semantic import SemanticIndex` is forbidden)

---

### FR-008: Incremental Update via FileWatcher

**Description:** The system shall support incremental index updates triggered by FileWatcher, delegating changed files to appropriate indexes for re-processing without full rebuild.

**Priority:** Medium

**Related User Stories:** Story 4

**Acceptance Criteria:**
- FileWatcher maps changed file paths to affected indexes (standards/, ouroboros/ → code)
- FileWatcher debounces changes (500ms window) to batch updates
- IndexManager provides `update_from_watcher(index_name, changed_files)` method
- Index.update() method re-processes only changed files (incremental, not full rebuild)
- For code index: update both semantic (re-chunk, re-embed) and graph (re-parse AST, update relationships)
- Update operations logged with file count and elapsed time

---

### FR-009: BaseIndex Abstract Interface

**Description:** The system shall define an abstract `BaseIndex` interface that all index submodules must implement, enforcing uniform method signatures and return types across all indexes.

**Priority:** Critical

**Related User Stories:** Story 1, Story 4

**Acceptance Criteria:**
- `BaseIndex` abstract class in `rag/base.py` with `@abstractmethod` decorators
- Required methods: `build(source_paths, force)`, `search(query, n_results, filters)`, `update(changed_files)`, `health_check()`, `get_stats()`
- Return types standardized: `search()` returns `List[SearchResult]`, `health_check()` returns `HealthStatus`
- All container classes inherit from `BaseIndex` and implement all abstract methods
- IndexManager type hints use `BaseIndex` (depends on abstraction, not concrete implementations)
- Python runtime raises `TypeError` if container doesn't implement required methods

---

### FR-010: Health Check Three-Tier Validation

**Description:** The system shall implement three-tier health check validation (metadata → functional → data integrity) to detect corruption early and enable startup auto-repair.

**Priority:** High

**Related User Stories:** Story 5

**Acceptance Criteria:**
- Tier 1 (Metadata): Check table exists, row count > 0
- Tier 2 (Functional): Execute test vector search, test FTS query, test scalar filter
- Tier 3 (Data Integrity): Validate row count >= expected minimum for source files
- Failed tier returns `HealthStatus(healthy=False, details={"needs_full_rebuild": True})`
- Partial corruption (FTS broken, vector OK) returns `details={"needs_secondary_rebuild": True}` for fast recovery
- Health check execution time < 5 seconds per index
- Health check results logged with ✅/⚠️/❌ emoji indicators

---

## 4.1 Requirements by Category

### Index Architecture & Discovery
- FR-001 (Uniform Container Entry Point)
- FR-002 (Registry-Based Index Discovery)
- FR-007 (Independent Submodule Internals)
- FR-009 (BaseIndex Abstract Interface)

### Reliability & Corruption Prevention
- FR-003 (File-Based Lock for Corruption Prevention)
- FR-005 (Corruption Detection and Auto-Repair)
- FR-010 (Health Check Three-Tier Validation)

### Database & Infrastructure
- FR-004 (Database Consolidation)
- FR-006 (Shared Utility Modules)

### Performance & Maintenance
- FR-008 (Incremental Update via FileWatcher)

---

## 4.2 Traceability Matrix

| Requirement | User Stories | Business Goals | Priority |
|-------------|--------------|----------------|----------|
| FR-001 | Story 1, 4 | Goal 4 (Predictable Discovery) | Critical |
| FR-002 | Story 2 | Goal 1 (Independent Evolution) | Critical |
| FR-003 | Story 3 | Goal 2 (Eliminate Corruption) | Critical |
| FR-004 | Story 6 | Goal 3 (Simplify Database) | High |
| FR-005 | Story 5 | Goal 2 (Eliminate Corruption) | High |
| FR-006 | Story 4 | Goal 3 (Simplify Database) | High |
| FR-007 | Story 4 | Goal 1 (Independent Evolution) | High |
| FR-008 | Story 4 | Goal 1 (Independent Evolution) | Medium |
| FR-009 | Story 1, 4 | Goal 1, 4 (Evolution + Discovery) | Critical |
| FR-010 | Story 5 | Goal 2 (Eliminate Corruption) | High |

---

## 4.3 Supporting Documentation

Requirements informed by:
- **RAG Index Submodule Pattern Design Doc**: Detailed architecture, interface design, file locking implementation, corruption detection patterns, utility module specifications, and migration path from current 3-file split (ast_index.py, graph_index.py, code_index.py) to unified submodule pattern

See `supporting-docs/INDEX.md` for complete requirements extraction from design insights.

---

## 5. Non-Functional Requirements


### 5.1 Performance

**NFR-P1: Health Check Response Time**
- Health check execution: < 5 seconds per index
- Startup health check (all indexes): < 15 seconds total
- Rationale: Fast startup feedback, no perceived delay

**NFR-P2: Index Build Time**
- Standards index rebuild: < 2 minutes (baseline: current ~2-3 min)
- Code index rebuild: < 3 minutes (improvement via single-pass DuckDB vs SQLite+DuckDB)
- Incremental update (FileWatcher): < 10 seconds for 1-10 changed files
- Rationale: Faster iteration during development

**NFR-P3: Query Response Time**
- Semantic search (vector+FTS): p95 < 200ms
- Structural search (AST): p95 < 100ms  
- Graph traversal (find_callers, depth=10): p95 < 500ms
- Rationale: Interactive query performance for AI/human users

---

### 5.2 Reliability

**NFR-R1: Corruption Prevention**
- Corruption incidents from concurrent access: 0 per month (baseline: 2-3/week)
- File lock acquisition success rate: 100% (fail fast with actionable error)
- Rationale: "Just works" reliability, no manual intervention needed

**NFR-R2: Auto-Repair Success Rate**
- Startup auto-repair success: 100% for detectable corruption patterns
- Runtime auto-repair success: 95%+ (retry once after rebuild)
- Repair time: < 60 seconds for standards index, < 120 seconds for code index
- Rationale: Transparent recovery, user never sees corruption errors

**NFR-R3: Index Build Success Rate**
- First-time build success: 100% (no corruption during build)
- Rebuild after corruption: 100% (repeatable, deterministic)
- Rationale: Predictable, reliable operations

**NFR-R4: Data Integrity**
- Index row count matches source files: ± 5% tolerance (accounts for filtered files)
- No data loss during incremental updates
- All changed files reflected in index within 1 minute (FileWatcher + debounce)
- Rationale: Index accurately represents source data

---

### 5.3 Maintainability

**NFR-M1: Code Reuse via Shared Utilities**
- Database connection code duplication: < 50 lines total (baseline: ~200 lines across 3 files)
- Utility module usage: 100% of indexes use `LanceDBConnection`, `EmbeddingModelLoader`
- Rationale: DRY principle, single source of truth for common operations

**NFR-M2: Test Coverage**
- Unit test coverage: minimum 80% for new submodule code
- Integration test coverage: 100% of critical paths (lock acquisition, auto-repair, registry discovery)
- Mock-based tests for corruption scenarios (simulate LanceDB errors)
- Rationale: Regression prevention, confident refactoring

**NFR-M3: Code Complexity**
- IndexManager special-case branches: 0 (baseline: 4+ branches for ast/graph special handling)
- Container.py file size: < 300 lines per index (simple delegation, not implementation)
- Cyclomatic complexity: < 10 per method
- Rationale: Readable, understandable code

**NFR-M4: Documentation and Discoverability**
- Every submodule has docstring explaining purpose and architecture
- Container.py methods have clear docstrings with Args, Returns, Raises
- README or architecture doc explains submodule pattern with examples
- Rationale: Onboarding < 15 minutes (baseline: ~1 hour)

---

### 5.4 Scalability

**NFR-SC1: Index Addition Scalability**
- Time to add new index: < 30 minutes (baseline: ~4 hours)
- Steps required: 3 (create submodule, add registry entry, add config)
- IndexManager code changes: 0 lines (registry handles discovery)
- Rationale: Easy extension without central bottleneck

**NFR-SC2: Concurrent Query Support**
- Support concurrent queries from multiple clients (stdio + http)
- Shared lock allows unlimited readers
- No query interference or resource contention
- Rationale: Multi-client MCP server usage

---

### 5.5 Portability

**NFR-PT1: Platform Support**
- POSIX systems (Linux, macOS): Full file locking support via fcntl
- Windows: Graceful degradation (stub implementation, log warning, no hard failure)
- Python 3.10+: Compatibility with modern type hints and async patterns
- Rationale: Broad platform support, graceful degradation

**NFR-PT2: Database Portability**
- LanceDB: Use stable 0.13.0+ API (avoid unreleased features)
- DuckDB: Use stable 0.9.0+ API
- No vendor-specific SQL extensions in DuckDB queries
- Rationale: Upgrade safety, dependency stability

---

### 5.6 Usability

**NFR-U1: Error Messages (Actionable)**
- All errors include: what_failed, why_failed, how_to_fix
- Lock acquisition failure: Specific message "MCP server running, close Cursor first"
- Corruption detection: Logged with emoji indicators (⚠️/❌) and auto-repair status
- Rationale: Users know exactly how to fix issues

**NFR-U2: Logging and Observability**
- Structured logging with standard format: timestamp, level, component, message
- Health check results logged with visual indicators (✅ healthy, ⚠️ unhealthy)
- Auto-repair operations logged with before/after status
- Rationale: Debuggable, observable system behavior

---

### 5.7 Testability

**NFR-T1: Unit Test Isolation**
- Every index can be tested independently (no shared state)
- Mock dependencies (LanceDB, DuckDB, filesystem) for fast tests
- Test suite runs in < 30 seconds (no real index building in unit tests)
- Rationale: Fast feedback loop, confident refactoring

**NFR-T2: Integration Test Coverage**
- Test startup corruption recovery (corrupt index → auto-rebuild → healthy)
- Test lock behavior (shared allows multiple, exclusive blocks all)
- Test registry discovery (add new index → auto-initialized)
- Rationale: Critical paths validated end-to-end

**NFR-T3: Corruption Scenario Testing**
- Mock LanceDB errors ("lance error", "invalid manifest", "corrupted")
- Verify detection triggers auto-repair
- Verify repair succeeds and retries search
- Rationale: Reliable auto-repair under all corruption patterns

---

### 5.8 Security

**NFR-SEC1: File System Security**
- Index files created with restricted permissions (600 for lock files, 644 for data)
- No sensitive data in index files (embeddings and metadata only)
- Advisory locks (fcntl) respect well-behaved processes
- Rationale: Basic file security, prevent unauthorized access

**NFR-SEC2: Dependency Security**
- Pin dependency versions (LanceDB >=0.13.0, DuckDB >=0.9.0)
- Regular security updates for dependencies
- No eval() or exec() in parsing/query logic (except controlled lambda in cross-field rules)
- Rationale: Supply chain security, code injection prevention

---

## 5.9 Supporting Documentation

NFRs informed by:
- **RAG Index Submodule Pattern Design Doc**: 
  - Performance targets from motivation (index addition 4hrs→30min, corruption 2-3/week→0/month)
  - Reliability requirements from corruption detection section (auto-repair, health checks)
  - Maintainability goals from shared utilities section (DRY, code reuse)
  - Testing strategy from testing section (unit, integration, mock-based)
  - Platform compatibility from file locking section (POSIX fcntl, Windows stub)

See `supporting-docs/INDEX.md` for complete NFR extraction from implementation insights.

---

## 6. Out of Scope


### Explicitly Excluded

#### Features

**Not Included in This Release:**

1. **Windows File Locking Implementation**
   - **Reason:** Windows-specific file locking (msvcrt/win32event) requires platform-specific testing infrastructure not currently available. Stub implementation provides graceful degradation.
   - **Future Consideration:** Phase 2 enhancement if Windows users report corruption issues

2. **Performance Benchmarking Suite**
   - **Reason:** Focus is architectural refactoring for maintainability and reliability, not query performance optimization. Baseline performance is maintained.
   - **Future Consideration:** Separate performance optimization project after migration stabilizes

3. **Migration Rollback Strategy**
   - **Reason:** One-way migration from old structure to new structure. Manual rollback (git revert) is sufficient for development phase.
   - **Future Consideration:** Not planned - migration is commit-once operation

4. **New Index Types (project_docs, dependency_docs)**
   - **Reason:** Refactoring existing indexes (standards, code) is sufficient to validate submodule pattern. New indexes add scope without validating architecture.
   - **Future Consideration:** Phase 2 addition after submodule pattern proven in production

5. **Query API Changes**
   - **Reason:** Tool layer API remains unchanged (backward compatibility). Internal routing changes are transparent to users.
   - **Future Consideration:** Not planned - stable API is feature

6. **Embedding Model Selection/Optimization**
   - **Reason:** Model selection (sentence-transformers) is orthogonal to architecture refactoring. Changing models adds testing complexity.
   - **Future Consideration:** Separate ML optimization project

7. **RAG Content Restructuring**
   - **Reason:** Standards and code content structure remains unchanged. Architecture refactoring doesn't require content migration.
   - **Future Consideration:** Not planned - content structure is stable

8. **Cross-Index Search**
   - **Reason:** Tool layer already supports sequential multi-index queries (search standards, then search code). Combined single query adds complexity without clear user need.
   - **Future Consideration:** Phase 3 if user demand emerges

---

#### Functionality Not Changed

**Stable/Unchanged Behavior:**

- **Search Query Syntax**: User-facing query syntax remains identical (natural language, filters, n_results)
- **Tool Layer Interfaces**: MCP tools (`pos_search_project`) maintain exact same signatures and return types
- **Index Build Sources**: Source file paths and discovery patterns unchanged (standards/, ouroboros/)
- **Embedding Models**: sentence-transformers models remain same (no re-embedding required)
- **Health Check Triggers**: Startup and runtime health check triggers unchanged (only implementation improves)

**Rationale:** Minimize user-facing changes, focus on internal architecture improvements

---

#### Performance Not Optimized

**Baseline Performance Maintained (Not Improved):**

- **Query Latency**: Vector search, FTS, graph traversal maintain baseline performance (no optimization work)
- **Index Build Parallelization**: Single-threaded build process unchanged (no async/parallel chunking)
- **Memory Usage**: No memory optimization work (lazy loading pattern unchanged)
- **Cache Strategies**: No query result caching or hot-path optimization

**Rationale:** Performance optimization is separate concern from architecture refactoring. Avoid conflating goals.

---

#### Platforms Not Fully Supported

**Limited Support:**

- **Windows File Locking**: Stub implementation only (no concurrency protection). Warning logged on startup. Full implementation deferred to Phase 2.
- **Python < 3.10**: Minimum Python 3.10 required (type hints, dataclasses, asyncio patterns). No backward compatibility for older Python versions.

**Rationale:** Graceful degradation acceptable for Windows (low adoption). Python 3.10+ is modern baseline.

---

#### Testing Scope Limitations

**Not Comprehensively Tested:**

- **Windows-Specific Behaviors**: No CI/CD pipeline for Windows file locking stub. Manual testing only if issues reported.
- **Concurrent Rebuild Stress Tests**: Basic lock tests included, but extreme concurrency (100+ simultaneous rebuilds) not stress-tested.
- **Large-Scale Index Tests**: Testing with realistic data sizes (~1000 standards docs, ~10,000 code files), not extreme scale (1M+ files).

**Rationale:** Focus testing on common scenarios and critical corruption paths. Extreme edge cases handled reactively.

---

#### Integrations Not Included

**External Systems Not Integrated:**

- **External RAG Services**: No integration with external vector databases (Pinecone, Weaviate, Qdrant). LanceDB remains only vector store.
- **Cloud Storage**: No S3/GCS/Azure integration for index storage. Local filesystem only.
- **Metrics/Monitoring Platforms**: No Datadog, Prometheus, or Grafana integration. Structured logging only.
- **CI/CD Automation**: Manual migration execution. No automated migration scripts or deployment pipelines.

**Rationale:** prAxIs OS is local-first, single-user system. External integrations add complexity without clear user benefit.

---

## 6.1 Future Enhancements

**Potential Phase 2 (After Production Validation):**

1. **Add project_docs Index** - Local project documentation search (docs/, README.md)
2. **Add dependency_docs Index** - External dependency documentation with versioning
3. **Windows File Locking** - Full msvcrt/win32event implementation if user demand
4. **Health Check Dashboard** - Web UI for index health status, rebuild triggers, metrics

**Potential Phase 3 (If User Demand):**

1. **Cross-Index Search** - Single query searches multiple indexes, merges results by relevance
2. **Query Result Caching** - Redis/in-memory cache for frequent queries
3. **Async/Parallel Index Building** - Speed up index builds with concurrent chunking/embedding
4. **Incremental Embedding Updates** - Partial model loading for faster incremental updates

**Explicitly Not Planned:**

- **Replace LanceDB** - LanceDB is proven, switching to alternative (Pinecone, Weaviate) adds migration complexity without clear benefit
- **GraphQL API** - REST/MCP tool interface is sufficient, GraphQL adds complexity
- **Multi-Tenancy** - prAxIs OS is single-user system, multi-tenancy fundamentally incompatible with design

---

## 6.2 Supporting Documentation

Out-of-scope items from:
- **RAG Index Submodule Pattern Design Doc**: 
  - Explicitly stated "performance benchmarking during initial migration" out of scope
  - Windows compatibility noted as "stub/no-op for now" (deferred implementation)
  - Migration rollback not covered (one-way migration)
  - New indexes (project_docs, dependency_docs) listed as "Future" not current phase

See `supporting-docs/INDEX.md` for boundary clarifications from design sections.

---

## 7. Approval and Sign-Off

**Requirements Review:**
- [ ] Business stakeholder approval
- [ ] Technical lead approval
- [ ] Security review (if applicable)

**Next Phase:**
Upon approval, proceed to Phase 2 (Design) to create detailed technical design for implementing these requirements.

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-04  
**Status:** Draft (Awaiting Review)

