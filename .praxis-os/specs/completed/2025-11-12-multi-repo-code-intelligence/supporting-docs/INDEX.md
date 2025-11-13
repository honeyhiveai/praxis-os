# Supporting Documents Index

**Spec:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Created:** 2025-11-12  
**Total Documents:** 1

## Document Catalog

### 1. Multi-Repo Code Intelligence Design Document

**File:** `2025-11-11-multi-repo-code-intelligence-instrumentor-analysis.md`  
**Type:** Design Document  
**Size:** 91 KB  
**Purpose:** Comprehensive design for extending prAxIs OS code intelligence to support multiple external repositories (OpenTelemetry instrumentors) with partition-based scaling and automated semantic convention extraction workflows.

**Relevance:** Requirements [H], Design [H], Implementation [H]

**Key Topics:**
- Multi-repo indexing architecture (primary + instrumentors partitions)
- Partition-based scaling strategy (437K chunks across 270 instrumentors)
- Dynamic partition lifecycle management (CRUD operations)
- Repository tracking and synchronization
- Cross-repo graph traversal (configurable per partition)
- AST/semantic/graph index partitioning
- Instrumentor analysis workflows (semantic convention extraction)
- Parse-once, index-thrice optimization
- Integration with Cascading Health Check Architecture
- Incremental per-repo rebuilds
- Git sync + repository tracker components

**Target Use Case:**
- **Primary:** Extract semantic conventions from OpenTelemetry instrumentors for HoneyHive ingestion service
- **Secondary:** General multi-repo code analysis for monorepos, dependencies, reference codebases

**Scale Projections:**
- Primary partition: 113K chunks (prAxIs OS + python-sdk)
- Instrumentors partition: 324K chunks (270 instrumentors across 3 providers)
- Total: 437K chunks (well within single-table limits)

**Key Design Decisions:**
1. **Hybrid Partitioning:** Primary (user's code) + Instrumentors (external analysis) for operational separation
2. **Config-Driven:** All partitions dynamically discovered from `mcp.yaml`, zero hardcoding
3. **All-3-Indexes:** Semantic, AST, and Graph all partitioned consistently
4. **Health Check Integration:** Fractal 4-level hierarchy (CodeIndex → Partition → Index Type → Sub-components)
5. **Soft Delete:** Archive partition data instead of hard delete for rollback capability

**Dependencies Referenced:**
- Cascading Health Check Architecture (2025-11-08): 4-level fractal health checks
- AST-Aware Code Chunking (2025-11-10): Config-driven AST parsing, import penalty

---

## Cross-Document Analysis

**Common Themes:**
- N/A (single document)

**Potential Conflicts:**
- None identified

**Coverage Gaps:**
- Implementation details will need to be fleshed out in spec
- Testing strategy needs expansion
- Migration/rollback procedures need detailed steps
- Repository sync scheduling/cron details need specification
- Specific query workflow implementation patterns

---

## Design Document Sections

The design document contains comprehensive coverage across:

### 1. Problem Statement (Section 1)
- Instrumentor analysis challenge
- Current manual process inefficiencies
- Pain points (3 hours per instrumentor, error-prone)

### 2. Current State (Section 2)
- Single-repo indexing limitations
- Existing infrastructure (Semantic, AST, Graph indexes)
- Config structure

### 3. Requirements (Section 3)
- Functional requirements (FR1-FR10)
- Non-functional requirements (NFR1-NFR6)
- Out of scope items

### 4. Proposed Solution (Section 4)
- Partition-based architecture overview
- Repository tracking
- Dynamic config-driven discovery
- Health check integration

### 5. Design Details (Section 5)
- Config schema updates (`mcp.yaml`)
- Schema changes (Semantic, AST, Graph indexes)
- Component architecture (RepositoryTracker, RepositorySyncer, IncrementalIndexer)
- Partition lifecycle management (CRUD)
- Startup flow
- Health check output (4-level fractal)

### 6. Query Workflow Patterns (Section 6)
- Instrumentor analysis workflows
- Example queries (find set_attribute calls, span naming, etc.)
- Cross-repo patterns

### 7. Implementation Plan (Section 7)
- 7 phases with time estimates (25-30 hours total)
- Phase breakdown from config to workflows
- Testing requirements

### 8. Success Metrics (Section 8)
- Speed: 15 min vs 3 hours (12x improvement)
- Accuracy: 100% vs ~85% manual
- Operational: p95 < 200ms, rebuild < 5min
- Adoption: 5 instrumentors analyzed in first month

### 9. Dependencies (Section 9)
- Cascading Health Check Architecture
- AST-Aware Code Chunking
- Git, Tree-sitter, LanceDB, DuckDB

### 10. Risks and Mitigations (Section 10)
- Scale concerns (addressed)
- Schema drift (partition isolation)
- Git sync failures (error handling)
- Disk space (compression, cleanup)
- API rate limits (sparse checkout)

---

## Key Insights for Spec Creation

**For Requirements (srd.md):**
- User story: As a HoneyHive developer, I need to analyze instrumentor codebases...
- Functional requirements: Multi-repo indexing, partition management, repo tracking, cross-repo search
- Non-functional: Performance (p95 < 200ms), scale (437K chunks), maintainability

**For Design (specs.md):**
- Architecture: Partition-based CodeIndex with dynamic discovery
- Components: RepositoryTracker, RepositorySyncer, IncrementalIndexer, CodePartition
- Schemas: All 3 indexes get partition/repo_name/provider metadata
- APIs: Search with partition filtering, partition CRUD, repo sync operations

**For Implementation (tasks.md + implementation.md):**
- 7 implementation phases with clear dependencies
- Config-first approach (update mcp.yaml, then Pydantic schemas)
- Test strategy: Per-component unit tests + integration tests for full partition lifecycle
- Validation: Health checks at all levels

---

## Next Steps

This index will be used in Task 3 to systematically extract insights from the design document. The extracted insights will be organized by:
- **Requirements Insights:** User needs, business goals, functional requirements
- **Design Insights:** Architecture patterns, technical approaches, component designs  
- **Implementation Insights:** Code patterns, testing strategies, deployment guidance


---

## Extracted Insights

### Requirements Insights (Phase 1)

#### From Multi-Repo Code Intelligence Design Document:

**User Needs:**
- **Primary User:** HoneyHive developers analyzing OpenTelemetry instrumentor codebases
- **Pain Point:** Manual analysis takes 3 hours per instrumentor, error-prone, incomplete
- **Desired Outcome:** Automated extraction of semantic conventions in 15 minutes with 100% accuracy

**Business Goals:**
- Support 270 instrumentors across 4 providers (OpenLit, Traceloop, Arize, OpenTelemetry)
- Enable BYOI (Bring Your Own Instrumentor) feature with comprehensive framework support
- Reduce maintenance burden when instrumentors update (incremental re-analysis)
- Scale to monorepos and multi-project codebases beyond instrumentors

**Functional Requirements:**
- **FR-1:** Index multiple external Git repositories (not just user's own code)
- **FR-2:** Partition indexes (primary code vs instrumentors) for operational separation
- **FR-3:** Repository tracking (commit hash, last indexed time, state)
- **FR-4:** Incremental per-repo rebuilds (only changed files)
- **FR-5:** Cross-repo search with filtering by partition/repo/provider
- **FR-6:** Cross-repo call graph traversal (configurable per partition)
- **FR-7:** Automated semantic convention extraction workflows
- **FR-8:** YAML/JSON output generation for ingestion service mapping
- **FR-9:** Git repository synchronization (clone, pull, sparse checkout)
- **FR-10:** Partition lifecycle management (CRUD: create, read, update, delete)

**Non-Functional Requirements:**
- **NFR-1 Performance:** p95 query latency < 200ms, extraction workflow < 15 min per instrumentor
- **NFR-2 Storage:** Total disk < 3GB (primary < 500MB, instrumentors < 2GB), incremental indexing
- **NFR-3 Maintainability:** Query templates reusable, version-controlled extraction scripts
- **NFR-4 Reliability:** Graceful parse error handling, per-repo health checks, rollback capability
- **NFR-5 Scale:** Support 437K chunks (primary 113K + instrumentors 324K) with single-table architecture
- **NFR-6 Operability:** Soft delete for partitions (archive data, not hard delete), orphaned data detection

**Constraints:**
- Must integrate with existing Cascading Health Check Architecture
- Must leverage AST-Aware Code Chunking for partition metadata
- Must maintain backward compatibility with single-repo usage
- Git repos must be accessible (local clones or network access)

**Out of Scope:**
- Remote API-based indexing (GitHub API, GitLab API) - local clones only
- Language-specific analysis beyond Tree-sitter capabilities
- Real-time sync (batch/cron-based only for MVP)
- Cross-language call graphs (Python-only for MVP)

---

### Design Insights (Phase 2)

#### From Multi-Repo Code Intelligence Design Document:

**Architecture:**
- **Partition-Based Scaling:** CodeIndex contains multiple CodePartition objects (primary, instrumentors)
- **Dynamic Discovery:** Partitions auto-discovered from `mcp.yaml` config, zero hardcoding
- **All-3-Indexes:** Semantic, AST, and Graph all partitioned consistently with same metadata
- **Fractal Health Checks:** 4-level hierarchy (CodeIndex → Partition → Index Type → Sub-components)
- **Parse-Once-Index-Thrice:** Single Tree-sitter parse populates all 3 indexes for efficiency

**Components:**
1. **CodePartition:** Logical grouping of repositories with independent indexes and health checks
2. **RepositoryTracker:** Tracks state (commit hash, indexed time) for incremental updates
3. **RepositorySyncer:** Handles Git operations (clone, pull, sparse checkout)
4. **IncrementalIndexer:** Updates only changed files across all 3 indexes
5. **PartitionManager:** CRUD operations for partition lifecycle

**Config Schema (`mcp.yaml`):**
```yaml
indexes:
  code:
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
          semantic: {p95_ms: 150}
          ast: {p95_ms: 50}
          graph: {p95_ms: 100}
        graph_cross_repo: true  # Enable cross-repo edges within partition
      
      instrumentors:
        name: "OpenTelemetry Instrumentors"
        repositories:
          - name: "openai-instrumentation"
            url: "https://github.com/open-telemetry/opentelemetry-python-contrib"
            sparse_paths: ["instrumentation/opentelemetry-instrumentation-openai"]
            provider: "opentelemetry"
        performance_targets:
          semantic: {p95_ms: 200}
          ast: {p95_ms: 75}
          graph: {p95_ms: 150}
        graph_cross_repo: false  # Isolated per-repo graphs
```

**Schema Changes:**

**SemanticIndex (LanceDB):**
```python
# Add to existing chunk schema:
{
    "partition": str,        # "primary" or "instrumentors"
    "repo_name": str,        # "python-sdk"
    "provider": str,         # "honeyhive", "opentelemetry", "openlit", etc.
    # ... existing fields (chunk_id, content, file_path, chunk_type, etc.)
}
```

**ASTIndex (DuckDB `ast_nodes` table):**
```sql
ALTER TABLE ast_nodes ADD COLUMN partition TEXT;
ALTER TABLE ast_nodes ADD COLUMN repo_name TEXT;
ALTER TABLE ast_nodes ADD COLUMN provider TEXT;
```

**GraphIndex (DuckDB `symbols` and `relationships` tables):**
```sql
ALTER TABLE symbols ADD COLUMN partition TEXT;
ALTER TABLE symbols ADD COLUMN repo_name TEXT;
ALTER TABLE symbols ADD COLUMN provider TEXT;

ALTER TABLE relationships ADD COLUMN caller_repo TEXT;
ALTER TABLE relationships ADD COLUMN callee_repo TEXT;
-- ^ Enables filtering cross-repo edges based on partition config
```

**Data Models:**
- **CodePartition:** Manages sub-indexes (Semantic, AST, Graph), tracks repos, provides health checks
- **RepositoryState:** Tracks commit hash, indexed timestamp, file count, status
- **PartitionConfig:** Pydantic model for partition settings (from mcp.yaml)

**APIs:**
- **Search with Filtering:** `pos_search_project(..., filters={"partition": "instrumentors", "provider": "openlit"})`
- **Partition CRUD:** Create, read, update, delete partitions dynamically
- **Repository Sync:** `RepositorySyncer.sync_repository(repo_config)`
- **Incremental Index:** `IncrementalIndexer.update_changed_files(repo_name, changed_files)`
- **Health Check:** `CodePartition.health_check()` returns fractal component tree

**Lifecycle Management:**
- **Create Partition:** Detect new partition in config → create directories → init tables → full build
- **Update Partition (Add Repo):** Incremental index of new repo across all 3 indexes
- **Update Partition (Remove Repo):** Atomic deletion of all chunks/nodes/symbols for that repo
- **Delete Partition (Soft):** Archive index data to `.archive/{partition_name}_{timestamp}/` for rollback
- **Delete Partition (Hard):** Permanent removal of index directories and tables
- **Orphaned Data Detection:** Startup validation checks for index data without config entry
- **Config Validation:** Check valid paths, no duplicate repos, valid partition names

**Security:**
- Git credentials via SSH keys or environment variables (not in config files)
- Path validation to prevent directory traversal
- Sparse checkout to limit disk exposure

---

### Implementation Insights (Phase 4)

#### From Multi-Repo Code Intelligence Design Document:

**Implementation Plan (7 Phases, 25-30 hours):**

**Phase 0: Config & Schema (3-4 hours)**
- Update `mcp.yaml` with partition structure
- Update Pydantic schemas (`CodeIndexConfig`, add `PartitionConfig`)
- Add partition/repo_name/provider columns to all 3 index schemas
- Validate config loading and schema migrations

**Phase 1: Repository Tracking (3-4 hours)**
- Implement `RepositoryTracker` class (DuckDB table: `repository_state`)
- Track commit hash, indexed timestamp, file count, status
- Implement `RepositorySyncer` for Git operations (clone, pull, sparse checkout)
- Test sync on single repo

**Phase 2: CodePartition Container (4-5 hours)**
- Implement `CodePartition` class wrapping 3 sub-indexes
- Dynamic partition discovery from config
- Partition-level health checks (fractal ComponentDescriptor)
- Partition-specific build/update methods

**Phase 3: Incremental Indexing (5-6 hours)**
- Implement `IncrementalIndexer` for changed-file detection
- Update Semantic, AST, Graph indexes atomically for changed files
- Test incremental updates (add file, modify file, delete file)
- Verify parse-once-index-thrice optimization

**Phase 4: Partition Lifecycle (4-5 hours)**
- Implement CRUD operations (create, update, delete partitions)
- Soft delete with archival
- Orphaned data detection
- Startup validation and config checks

**Phase 5: Cross-Repo Queries (3-4 hours)**
- Update search APIs to support partition/repo/provider filtering
- Implement cross-repo graph traversal (config-driven)
- Test queries across partitions
- Validate performance (p95 < 200ms)

**Phase 6: Query Workflows (3-4 hours)**
- Implement extraction templates (span attributes, naming patterns)
- Output generators (YAML/JSON for ingestion service)
- Test on 3 sample instrumentors (FastAPI, LangChain, OpenAI)
- Document workflow patterns

**Code Patterns:**

**Dynamic Partition Discovery:**
```python
class CodeIndex(BaseIndex):
    def __init__(self, config: CodeIndexConfig, base_path: Path):
        self.partitions: Dict[str, CodePartition] = {}
        
        # Dynamic discovery from config
        for partition_name, partition_config in config.partitions.items():
            self.partitions[partition_name] = CodePartition(
                name=partition_name,
                config=partition_config,
                base_path=base_path
            )
```

**Health Check (Fractal 4-Level):**
```python
def health_check(self) -> HealthStatus:
    """CodeIndex → Partitions → Index Types → Sub-components."""
    partition_health = {}
    for name, partition in self.partitions.items():
        partition_health[name] = partition.health_check()  # Recursive
    
    return HealthStatus(
        healthy=all(h.healthy for h in partition_health.values()),
        components=partition_health
    )
```

**Incremental Update:**
```python
def update_repository(self, repo_name: str):
    """Incremental update for single repo across all 3 indexes."""
    # 1. Git pull
    new_commit = self.syncer.pull(repo_name)
    
    # 2. Detect changed files
    changed = self.tracker.get_changed_files(repo_name, new_commit)
    
    # 3. Parse once with Tree-sitter
    for file in changed:
        tree = parse_file(file)
        
        # 4. Index thrice (Semantic, AST, Graph)
        self.semantic.update_file(file, tree)
        self.ast.update_file(file, tree)
        self.graph.update_file(file, tree)
    
    # 5. Update tracker
    self.tracker.record_sync(repo_name, new_commit)
```

**Testing Strategy:**
- **Unit Tests:** Each component (RepositoryTracker, RepositorySyncer, CodePartition) with mocks
- **Integration Tests:** Full partition lifecycle (create, add repo, query, delete)
- **Performance Tests:** Verify p95 latency < 200ms with 437K chunks
- **Scale Tests:** Load 270 instrumentors, verify query performance
- **Regression Tests:** Ensure single-repo usage still works (backward compatibility)

**Deployment Guidance:**
- Start with single partition (primary) to validate
- Add instrumentors partition incrementally (test with 3-5 repos first)
- Monitor disk usage and query latency
- Use soft delete for first few partition removals (verify archive/restore)
- Document cron schedule for repository sync (e.g., daily at 2am)

**Error Handling:**
- Git sync failures: Log error, mark repo as "sync_failed", continue with other repos
- Parse errors: Log warning, skip file, don't block entire repo
- Schema drift: Validate partition/repo_name fields on all queries, fail fast with actionable error
- Orphaned data: Warn at startup, provide cleanup command, don't auto-delete

**Performance Optimizations:**
- Sparse checkout for large instrumentor repos (only index specific subdirectories)
- Incremental indexing (only changed files, not full repo)
- Parse-once-index-thrice (single Tree-sitter parse for all 3 indexes)
- Per-partition performance targets (fast queries on primary, acceptable on instrumentors)
- Background sync (don't block queries during repository updates)

---

## Cross-References

**Validated by Multiple Sections:**
- Partition-based architecture mentioned in Requirements (FR-2), Design (4.1), Implementation (Phase 2)
- Health check integration referenced in Requirements (NFR-4), Design (ComponentDescriptor), Implementation (fractal checks)
- Incremental indexing emphasized in Requirements (NFR-2), Design (IncrementalIndexer), Implementation (Phase 3)
- Performance targets (p95 < 200ms) in Requirements (NFR-1), Design (config schema), Implementation (Phase 5 validation)

**Conflicts:**
- None identified

**High-Priority Items:**
1. Config schema updates (Phase 0) - foundational for all other work
2. Repository tracking (Phase 1) - enables incremental indexing
3. Partition lifecycle (Phase 4) - operationally critical for production use
4. Performance validation (Phase 5) - must meet p95 < 200ms target

---

## Insight Summary

**Total:** 47 insights  
**By Category:** Requirements [18], Design [19], Implementation [10]  
**Multi-source validated:** 4 (partition architecture, health checks, incremental indexing, performance targets)  
**Conflicts to resolve:** 0  
**High-priority items:** 4 (config, repo tracking, partition lifecycle, performance)

**Insight Quality:**
- ✅ Specific and measurable (p95 < 200ms, 437K chunks, 3 hours → 15 min)
- ✅ Actionable with clear implementation steps (7-phase plan)
- ✅ Traceable to design doc sections
- ✅ Properly categorized (Requirements/Design/Implementation)

**Phase 0 Complete:** ✅ 2025-11-12

