# Requirements Traceability Matrix

**Project:** Multi-Repo Code Intelligence for Instrumentor Analysis  
**Date:** 2025-11-12  
**Purpose:** Complete list of all requirements with traceability to test cases

---

## Functional Requirements (FR)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| FR-001 | Multi-Repository Indexing | System must index multiple external Git repositories (not just user's own code) | FT-001, FT-002 | P0 |
| FR-002 | Partition Management | System must support partition-based index organization (primary code vs. instrumentors) | FT-003, FT-004, FT-005 | P0 |
| FR-003 | Repository State Tracking | System must track repository state (commit hash, last indexed time, status) for incremental updates | FT-006, FT-007 | P0 |
| FR-004 | Incremental Indexing | System must support incremental per-repository rebuilds (only changed files) | FT-008, FT-009 | P0 |
| FR-005 | Cross-Repository Query Filtering | System must support cross-repo search with filtering by partition/repo/provider | FT-010, FT-011, FT-012 | P0 |
| FR-006 | Cross-Repo Call Graph Traversal | System must support cross-repo call graph traversal (configurable per partition via `graph_cross_repo` flag) | FT-013, FT-014 | P1 |
| FR-007 | Git Repository Synchronization | System must support Git operations (clone, pull, sparse checkout) with authentication via SSH keys or environment variables | FT-015, FT-016, FT-017 | P0 |
| FR-008 | Semantic Convention Extraction | System must provide automated extraction workflows for span attributes and naming patterns | FT-018, FT-019 | P0 |
| FR-009 | Machine-Readable Output | System must generate YAML/JSON output for ingestion service mapping | FT-020 | P0 |
| FR-010 | Partition Lifecycle Management | System must support CRUD operations for partitions (create, read, update, delete with soft delete option) | FT-021, FT-022, FT-023, FT-024 | P1 |

**Total Functional Requirements:** 10

---

## Non-Functional Requirements (NFR)

### Performance (P)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-P1 | Primary Partition Query Latency | p95 query latency < 50ms for primary partition | NFT-001 | P0 |
| NFR-P2 | Instrumentors Partition Query Latency | p95 query latency < 200ms for instrumentors partition | NFT-002 | P0 |
| NFR-P3 | Extraction Workflow Duration | Extraction workflow completes in < 15 minutes per instrumentor | NFT-003 | P0 |
| NFR-P4 | Incremental Index Update Speed | Incremental index update < 5 seconds for 10 changed files | NFT-004 | P0 |
| NFR-P5 | Cold Start Time | Cold start index build < 10 minutes for 270 instrumentors | NFT-005 | P1 |

### Storage (ST)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-ST1 | Total Disk Usage | Total disk usage < 3GB (primary < 500MB, instrumentors < 2GB, margins < 500MB) | NFT-006 | P0 |
| NFR-ST2 | Incremental Storage | Incremental indexing doesn't duplicate entire repository data | NFT-007 | P1 |

### Maintainability (M)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-M1 | Extraction Template Reusability | Query templates for extraction workflows are reusable across instrumentors | NFT-008 | P1 |
| NFR-M2 | Version-Controlled Outputs | Extraction script outputs are version-controlled (YAML/JSON in Git) | NFT-009 | P1 |

### Reliability (R)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-R1 | Parse Error Handling | System gracefully handles parse errors (skip file, log warning, continue with repo) | NFT-010 | P0 |
| NFR-R2 | Per-Repo Health Checks | System provides per-repository health checks with error details | NFT-011 | P1 |
| NFR-R3 | Rollback Capability | System supports rollback to previous index state in < 2 minutes via soft delete | NFT-012 | P0 |
| NFR-R4 | Sync Failure Isolation | Git sync failures for one repo don't block other repos | NFT-013 | P0 |

### Scalability (S)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-S1 | Scale to 270 Instrumentors | System supports 270 instrumentors across 4 providers (OpenLit, Traceloop, Arize, OpenTelemetry) | NFT-014 | P0 |
| NFR-S2 | Single-Table Architecture | System uses single-table architecture with partition metadata (no separate DBs per partition) | NFT-015 | P1 |
| NFR-S3 | Total Chunk Scale | System supports 437K total chunks (primary 113K + instrumentors 324K) | NFT-016 | P0 |
| NFR-S4 | Parse Error Rate | Parse error rate < 5% of total files | NFT-017 | P1 |

### Operability (O)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-O1 | Soft Delete with Archival | System archives partition data to `.archive/{partition}_{timestamp}/` for rollback | NFT-018 | P0 |
| NFR-O2 | Orphaned Data Detection | System detects orphaned data at startup and warns user (no auto-delete) | NFT-019 | P1 |
| NFR-O3 | Partition Migration | System supports moving repositories between partitions (fast metadata update vs. slow re-index) | NFT-020 | P2 |
| NFR-O4 | Config Validation | System validates config on load (valid paths, no duplicate repos, valid partition names, no embedded credentials) | NFT-021 | P0 |

### Security (Implicit)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-SEC1 | No Embedded Credentials | System rejects config with embedded credentials in URLs | NFT-022 | P0 |
| NFR-SEC2 | Path Traversal Prevention | System validates paths to prevent directory traversal attacks | NFT-023 | P0 |
| NFR-SEC3 | Error Message Safety | Error messages don't leak sensitive paths or credentials | NFT-024 | P1 |

### Integration (I)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-I1 | Cascading Health Check Integration | System integrates with Cascading Health Check Architecture (4-level fractal hierarchy) | NFT-025 | P0 |
| NFR-I2 | AST-Aware Chunking Integration | System leverages AST-Aware Code Chunking for partition metadata | NFT-026 | P0 |
| NFR-I3 | Backward Compatibility | System maintains backward compatibility with single-repo usage | NFT-027 | P0 |

### Performance Benchmarks (Targets)

| ID | Requirement | Description | Test Case(s) | Priority |
|----|-------------|-------------|--------------|----------|
| NFR-PB1 | Sync Success Rate | Git sync success rate > 95% across all repositories | NFT-028 | P1 |
| NFR-PB2 | Parse-Once Efficiency | Parse-once-index-thrice is >= 2x faster than parsing 3 times | NFT-029 | P1 |

**Total Non-Functional Requirements:** 29 (across 8 categories)

---

## Requirements Summary

**Total Requirements:** 39 (10 FR + 29 NFR)

**By Priority:**
- P0 (Critical): 22 requirements (7 FR + 15 NFR)
- P1 (High): 14 requirements (3 FR + 11 NFR)
- P2 (Medium): 3 requirements (0 FR + 3 NFR)

**Test Coverage:**
- Functional Tests: 27 test cases covering 10 FR
- Non-Functional Tests: 29 test cases covering 29 NFR
- Total Test Cases: 56

**Traceability:**
- 100% of requirements have associated test cases
- Every test case traces back to 1+ requirements
- No orphaned tests or untested requirements

---

